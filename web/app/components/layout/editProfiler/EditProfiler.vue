<script setup lang="ts">

  import type { User } from '~/types/user';

  const emit = defineEmits<{
    close: [];
  }>();

  const isPanelActive = ref(false);
  const verifyVisible = ref(false);

  const auth = useAuthStore();
  const eventsStore = useEventsStore();
  const api = useApi();
  const notifications = useNotificationsStore();
  
  const originalEmail = ref('');
  const username = ref('');
  const email = ref('');
  const currentPassword = ref('');
  const newPassword = ref('');

  const fieldErrors = ref({
    username: '',
    email: '',
    currentPassword: '',
    newPassword: '',
    code: '',
  });

  const formError = ref('');
  const isSubmitting = ref(false);
  const pendingNewEmail = ref('');
  const verificationCode = ref(''); 


  const isEmailChanged = computed(() =>
    email.value.trim().toLowerCase() !== originalEmail.value.toLowerCase(),
  );

  const isVerifyMode = computed(() => verifyVisible.value);

  const submitButtonLabel = computed(() =>
    isVerifyMode.value ? 'Verify' : 'Save Changes',
  );

  const isSubmitDisabled = computed(() => {
    if (isSubmitting.value) return true;
    if (isVerifyMode.value) return verificationCode.value.length !== 6;
    return false;
  });


  function validateForm(): boolean {
    fieldErrors.value = { username: '', email: '', currentPassword: '', newPassword: '', code: '' };
    formError.value = '';

    if (username.value.trim().length < 3) {
      fieldErrors.value.username = 'At least 3 characters';
    }
    if (!/^[a-zA-Z0-9_ ]+$/.test(username.value.trim())) {
      fieldErrors.value.username = 'Only letters, numbers, spaces and _';
    }
    if (!email.value.trim()) {
      fieldErrors.value.email = 'Enter your email';
    }

    const wantsPasswordChange = currentPassword.value || newPassword.value;
    if (wantsPasswordChange) {
      if (!currentPassword.value) fieldErrors.value.currentPassword = 'Enter current password';
      if (newPassword.value.length < 8) fieldErrors.value.newPassword = 'At least 8 characters';
    }

    return !Object.values(fieldErrors.value).some(Boolean);
  };

  function closeModal() {
    isPanelActive.value = false;
    setTimeout(() => {
      emit('close')
  }, 300)
  };


  async function saveProfile() {
    if (!validateForm()) return;

    isSubmitting.value = true;
    formError.value = '';

    try {
      // 1. Username
      if (username.value.trim() !== auth.user?.username) {
        const updated = await api<User>('/users/me', {
          method: 'PATCH',
          body: { username: username.value.trim() },
        });
        auth.setUser(updated);
      }

      // 2. Password
      if (currentPassword.value && newPassword.value) {
        await api('/users/me/password', {
          method: 'PATCH',
          body: {
            current_password: currentPassword.value,
            new_password: newPassword.value,
          },
        });
        currentPassword.value = '';
        newPassword.value = '';
      }

      // 3. Email
      if (isEmailChanged.value) {
        await api('/users/me/email-change/request', {
          method: 'POST',
          body: { new_email: email.value.trim() },
        });

        pendingNewEmail.value = email.value.trim();
        verifyVisible.value = true;
        verificationCode.value = '';
        notifications.success('Code sent', `Check ${pendingNewEmail.value}`);
        return; // email ещё не сохранён — ждём Verify
      }

      notifications.success('Profile updated', 'Changes saved');
      closeModal();
    } catch (e) {
      const parsed = parseApiError(e);
      Object.assign(fieldErrors.value, parsed.fieldErrors);
      formError.value = parsed.formError;
    } finally {
      isSubmitting.value = false;
    }
  };

  async function confirmEmailChange() {
    if (verificationCode.value.length !== 6) {
      fieldErrors.value.code = 'Enter the full 6-digit code';
      return;
    }

    isSubmitting.value = true;
    fieldErrors.value.code = '';
    formError.value = '';

    try {
      const updated = await api<User>('/users/me/email-change/confirm', {
        method: 'POST',
        body: { token: verificationCode.value },
      });

      auth.setUser(updated);
      originalEmail.value = updated.email;
      email.value = updated.email;
      verifyVisible.value = false;
      pendingNewEmail.value = '';
      verificationCode.value = '';

      notifications.success('Email updated', 'Profile saved');
      closeModal();
    } catch (e) {
      const parsed = parseApiError(e);
      fieldErrors.value.code = parsed.fieldErrors.token ?? parsed.formError;
      formError.value = parsed.formError;
    } finally {
      isSubmitting.value = false;
    }
  };


  async function onSubmit() {
    if (isVerifyMode.value) {
      await confirmEmailChange();
      return;
    }
    await saveProfile();
  }

  onMounted(async () => {
    await nextTick();
    requestAnimationFrame(() => {
      isPanelActive.value = true;
    });

    await auth.fetchMe();
    await eventsStore.fetchStats();

    if (auth.user) {
      username.value = auth.user.username;
      email.value = auth.user.email;
      originalEmail.value = auth.user.email;
    }
  });

</script>

<template>
  <div 
    class="fixed z-100 top-0 left-0 
      flex flex-col items-center p-3
      overflow-hidden w-full h-full"
    @click.self="closeModal"
  >
    <div class="
      edit-profiler-panel
      flex flex-col w-full max-w-200 min-h-100
      bg-third rounded-md border border-solid border-fifth/50
      shadow-lg
      "
      :class="{ active: isPanelActive }"
    >
      <div class="flex items-center justify-between gap-1.5 px-5 py-3.5">
        <h2 class="text-xl font-semibold text-text-main">
          Edit Profiler
        </h2>

        <button @click="closeModal" class="transition-all transition-300 ease-in-out hover:rotate-90">
          <Icon name="akar-icons:cross" mode="svg" class="size-5 text-text-main" />
        </button>
      </div>

      <div 
        class="
          relative overflow-hidden
          flex gap-2.5 px-5 py-5
          bg-main rounded-md shadow-sm
        "
      >
        <div class="flex flex-col gap-2.5 w-full">
          <form @submit.prevent="onSubmit" class="flex flex-col gap-2.5 w-full">
            <UiInput
              v-model="username"
              type="text"
              label="Name"
              placeholder="Your Name"
              :error-message="fieldErrors.username"
              :disabled="isVerifyMode"
            />
            <UiInput
              v-model="email"
              type="email"
              label="Email"
              placeholder="Your Email"
              :error-message="fieldErrors.email"
              :disabled="isVerifyMode"
            />
            <UiInput
              v-model="currentPassword"
              type="password"
              label="Current Password"
              :error-message="fieldErrors.currentPassword"
              :disabled="isVerifyMode"
            />
            <UiInput
              v-model="newPassword"
              type="password"
              label="New Password"
              :error-message="fieldErrors.newPassword"
              :disabled="isVerifyMode"
            />
          </form>

          <p v-if="formError" class="mt-4 text-center text-lg text-error">
            {{ formError }}
          </p>
        </div>

        <div class="flex flex-col items-center justify-center gap-4 w-full max-w-[30%]">

          <div class="flex flex-col items-center gap-0.5">
            <p class="text-center text-sm font-medium text-text-main">
              Preview
            </p>
            <div 
              class="
                w-25 h-25 p-3
                bg-third rounded-full
              "
            >
              <svg 
                class="w-full h-full fill-text-main"
                xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 32 32">
                <path d="M0 0h32v32H0z" fill="none" />
                <g fill="">
                  <path d="m15.287 17.527l-.99 3.17a1.005 1.005 0 0 0 .97 1.303h1.466c.688 0 1.173-.662.97-1.304l-.99-3.17c-.213-.701-1.203-.701-1.426 0m-1.87 5.757c.747.39 1.637.612 2.583.612c.956 0 1.836-.222 2.583-.612c.256-.13.53.148.369.39A3.53 3.53 0 0 1 16 25.25a3.53 3.53 0 0 1-2.952-1.577c-.16-.232.114-.52.369-.39M11.542 15.4c-1.214 0-2.24.84-2.527 1.967a.512.512 0 0 0 .503.633h.8a1.664 1.664 0 1 1 3.209 0h.148a.428.428 0 0 0 .424-.504a2.61 2.61 0 0 0-2.557-2.096m8.916 0c1.214 0 2.24.84 2.527 1.967a.512.512 0 0 1-.503.633h-.8a1.664 1.664 0 0 0-1.61-2.108a1.65 1.65 0 0 0-1.658 1.665q0 .236.06.443h-.149a.428.428 0 0 1-.424-.504a2.6 2.6 0 0 1 2.557-2.096" />
                  <path d="M11.927 16.611a.947.947 0 0 1 .84 1.389h-1.679a1 1 0 0 1-.108-.443c0-.172.046-.334.127-.473a.295.295 0 0 0 .544-.164a.3.3 0 0 0-.105-.229a.95.95 0 0 1 .381-.08m7.347.421a.94.94 0 0 0-.16.525c0 .157.04.305.11.443h1.678a.947.947 0 0 0-1.182-1.325a.3.3 0 0 1-.17.545a.3.3 0 0 1-.276-.188m2.404-4.649c.575.181.955.483 1.282.767a.517.517 0 0 1-.68.78c-.293-.256-.543-.444-.913-.56c-.378-.12-.927-.176-1.824-.067a.517.517 0 1 1-.126-1.026c.983-.12 1.694-.072 2.26.106m-12.313.747l-.001.002a.517.517 0 0 0 .633.818l.005-.004l.03-.022q.045-.032.14-.09a4.14 4.14 0 0 1 2.585-.53a.517.517 0 1 0 .127-1.027a5.17 5.17 0 0 0-3.242.67a4 4 0 0 0-.253.166l-.016.012l-.006.004z" />
                  <path d="M27.415 8.07a4.33 4.33 0 0 0-2.363-1.96c-1.049-.36-1.949-1.05-2.522-2A4.34 4.34 0 0 0 18.822 2c-.604 0-1.177.13-1.701.35c-.712.31-1.513.31-2.225 0a4.5 4.5 0 0 0-1.71-.35c-1.553 0-2.908.82-3.68 2.05a5 5 0 0 1-2.58 2.07c-.164.058-.326.106-.487.155C5.62 6.52 4.836 6.758 4 8.07c-1 1.57-1.12 3.4-.23 4.71c.327.48.505 1.05.505 1.63l.001.67A4 4 0 0 0 3 18.01c0 1.161.494 2.206 1.284 2.937q-.013.519-.034 1.039c0 1.134.925 2.185 1.991 2.933a8.3 8.3 0 0 0 8.008 6.091h3.517a8.3 8.3 0 0 0 8.011-6.104c1.059-.748 1.973-1.792 1.973-2.92l-.002-1.07A4 4 0 0 0 29 18.01a4 4 0 0 0-1.287-2.939v-.661c0-.58.178-1.15.504-1.63c.94-1.35.068-3.18-.802-4.71M7.5 13.3c0-2.926 2.399-5.3 5.29-5.3h2.373a.24.24 0 0 1 .219.151l.007.018l.008.018a5.52 5.52 0 0 0 5.037 3.283h2.587a1.7 1.7 0 0 1 1.593 1.651l-.166 2.768l.887.149a2 2 0 0 1-.216 3.969l-.885.051l-.22 3.504a6.3 6.3 0 0 1-6.248 5.448H14.25A6.3 6.3 0 0 1 8 23.56l-.23-3.504l-.884-.05a2 2 0 0 1-.26-3.961l.254-.048l.62-.091z" />
                </g>
              </svg>
            </div>
          </div>

          <div class="flex flex-col items-center gap-2.5">
            <h4 class="text-center text-lg font-bold text-text-main">
              {{ username }}
            </h4>

            <ul class="flex flex-col items-center text-center text-md font-normal text-text-main">
              <li>
                Events created: <span class="font-bold">{{ eventsStore.createdCount }}</span>
              </li>
              <li>
                Joined events: <span class="font-bold">{{ eventsStore.joinedCount }}</span>
              </li>
            </ul>
          </div>

        </div>

        <Transition name="smooth-appearance">
          <div 
            v-if="verifyVisible"
            class="
              absolute top-0 left-0 w-full h-full
              flex flex-col items-center justify-center p-3
              bg-overlay
            "
          >
            <div 
              class="flex flex-col justify-center w-full h-full p-3
              bg-main rounded-md 
              "
            >
              <div class="flex flex-col gap-0.5 mb-8">
                <h2 class="text-3xl font-bold text-text-main">
                  OTP Verification
                </h2>
                <p class="text-lg text-text-main">
                  Enter the 6-digit code sent to <span class="font-semibold">{{ pendingNewEmail }}</span>
                </p>
              </div>
              
              <UiVerification
                v-model="verificationCode"
                label="Verification code"
                :length="6"
                :error-message="fieldErrors.code"
                :disabled="isSubmitting"
              />
            </div>
          </div>
        </Transition>
      </div>
      <div class="flex items-center justify-end gap-2.5 px-5 py-3.5">
        <UiButton style-type="cancel" @click="closeModal">
          Cancel
        </UiButton>
        <UiButton
          style-type="primary"
          :disabled="isSubmitDisabled"
          @click="onSubmit"
        >
          {{ submitButtonLabel }}
        </UiButton>
      </div>
    </div>
  </div>
</template>

<style lang="scss">

  .edit-profiler-panel {
    transform: translateY(-100%);
    opacity: 0;

    transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;

    &.active {
      transform: translateY(0);
      opacity: 1;
    }
  }

  .smooth-appearance-enter-active,
  .smooth-appearance-leave-active {
    transition: opacity 0.3s ease-in-out;
  }
  .smooth-appearance-enter-from,
  .smooth-appearance-leave-to {
    opacity: 0;
  }

</style>

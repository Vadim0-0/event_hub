<script setup lang="ts">

  // --- Props & Emits ---
  const props = defineProps<{
    email: string
  }>();

  const emit = defineEmits<{
    'switch-to-login': []
  }>();


  // --- Composables ---
  const auth = useAuthStore();
  const notifications = useNotificationsStore();
  const { secondsLeft, isCooldownActive, start } = useResendCooldown(60);


  // --- State ---
  const CODE_LENGTH = 6;
  const code = ref('');
  const fieldError = ref('');
  const formError = ref('');


  // --- UI flags ---
  const isCodeComplete = computed(() => code.value.length === CODE_LENGTH);

  const isConfirmDisabled = computed(() =>
    !isCodeComplete.value || auth.isLoading,
  );

  const isResendDisabled = computed(() =>
    isCooldownActive.value || auth.isLoading,
  );

  onMounted(() => start(60));


  // --- Handlers ---
  async function onSubmit() {
    fieldError.value = '';
    formError.value = '';

    if (!isCodeComplete.value) {
      fieldError.value = 'Enter the full 6-digit code';
      return;
    }

    try {
      await auth.verifyEmail({
        email: props.email,
        code: code.value,
      });

      notifications.success('Email verified', 'Welcome!');
    } catch (e) {
      const parsed = parseApiError(e);
      fieldError.value = parsed.fieldErrors.code ?? '';
      formError.value = parsed.formError;
    };
  };

  async function onResend() {
    if (isResendDisabled.value) return;

    formError.value = '';
    try {
      await auth.resendVerificationCode(props.email);
      start(60);
      notifications.success('Code sent', 'Check your email');
    } catch (e) {
      const status = (e as any)?.status ?? (e as any)?.response?.status;
      const detail = (e as any)?.data?.detail;

      if (status === 429 && detail?.retry_after) {
        start(detail.retry_after);
        formError.value = detail.message ?? 'Please wait before resending';
        return;
      };

      formError.value = parseApiError(e).formError;
    };
  };

  function onCancel() {
    emit('switch-to-login');
  };

</script>

<template>
  <form @submit.prevent="onSubmit">
    <div class="flex flex-col gap-0.5 mb-8">
      <h2 class="text-heading-lg font-bold text-text-main">
        OTP Verification
      </h2>
      <p class="text-lg text-text-main">
        Enter the 6-digit code sent to <span class="font-semibold">{{ email }}</span>
      </p>
    </div>
    <div class="mb-8">
      <UiVerification
        v-model="code"
        label="Verification code"
        :length="6"
        input-class="!bg-secondary"
        :error-message="fieldError"
        :disabled="auth.isLoading"
      />
    </div>

    <div class="flex items-center justify-center gap-2 mb-4">
      <UiButton
        type="button"
        style-type="primary"
        class="w-11 h-11 !py-0"
        :disabled="isResendDisabled"
        @click="onResend"
      >
        <Icon name="fluent:arrow-sync-12-regular" mode="svg" class="w-[100%] h-[100%]" :class="{ 'animate-spin': auth.isLoading }"/>
      </UiButton>

      <p v-if="isCooldownActive" class="text-center text-lg text-text-main">
        You can resend OTP in <span>{{ secondsLeft }}</span> sec
      </p>
      <p v-else class="text-center text-lg text-text-main">
        Didn't receive the code? Click to resend
      </p>
    </div>

    <div class="grid grid-cols-2 gap-4 mb-4">
      <UiButton
        type="button"
        style-type="cancel"
        class="!py-3 !text-body-xl"
        @click="onCancel"
      >
        Cancel
      </UiButton>
      <UiButton
        type="submit"
        class="!py-3 !text-body-xl"
        :disabled="isConfirmDisabled"
      >
        Confirm
      </UiButton>
    </div>
    
    <p v-if="formError" class="mt-4 text-center text-lg text-error">
      {{ formError }}
    </p>
  </form>
</template>

<style scoped lang="scss">

</style>
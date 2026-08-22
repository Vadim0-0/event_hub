<script setup lang="ts">
  import { mapAuthPage } from '~/mappers/pages/authPage';

  type AuthPageMapped = ReturnType<typeof mapAuthPage>;

  const emit = defineEmits<{
    'switch-to-register': []
    'switch-to-verify': [email: string]
  }>();

  const props = defineProps<{
    content: AuthPageMapped['login']
  }>();

  const auth = useAuthStore();
  const email = ref('');
  const password = ref('');
  const fieldErrors = ref({ email: '', password: '' });
  const formError = ref('');

  const notifications = useNotificationsStore();
  const needsVerification = ref(false);

  async function onSubmit() {
    fieldErrors.value = { email: '', password: '' };
    formError.value = '';
    needsVerification.value = false

    if (!email.value) fieldErrors.value.email = props.content.errors.emailEmpty
    if (!password.value) fieldErrors.value.password = props.content.errors.passwordEmpty
    if (fieldErrors.value.email || fieldErrors.value.password) return

    try {
      await auth.login({ email: email.value, password: password.value })

      notifications.success(
        props.content.notifications.success.title,
        props.content.notifications.success.text.replace('{email}', email.value),
      );
    } catch (e: any) {
      const status = e?.status ?? e?.response?.status;
      const detail = e?.data?.detail;


      if (status === 403 && detail === 'Email is not verified') {
        formError.value = props.content.errors.notVerify
        notifications.success(
          props.content.notifications.send.title,
          props.content.notifications.send.text,
        );
        await auth.resendVerificationCode(email.value)
        emit('switch-to-verify', email.value)
        return
      };
      formError.value = detail || props.content.errors.general;
    };
  };

</script>

<template>
  <form @submit.prevent="onSubmit">
    <div class="mb-8">
      <h2 class="text-heading-lg font-bold text-text-main">
        {{ content.title }}
      </h2>
    </div>
    <div class="flex flex-col gap-4 mb-6">
      <UiInput 
        v-model="email"
        type="email"
        :placeholder="content.emailPlaceholder"
        :error-message="fieldErrors.email" 
        input-class="!bg-secondary"
      />
      <UiInput 
        v-model="password"
        type="password"
        :placeholder="content.passwordPlaceholder"
        :error-message="fieldErrors.password"
        input-class="!bg-secondary"
      />
    </div>
    <div class="grid grid-cols-2 gap-4 mb-6">
      <NuxtLink to="/" 
        class="
          btn-global py-3 
          
          bg-fourth text-text-main border border-solid border-fifth
          hover:bg-third
        "
      >
        {{ content.cancelButton }}
      </NuxtLink>
      <UiButton
        type="submit"
        :disabled="auth.isLoading"
        class="!py-3 !text-body-xl"
      >
        {{ auth.isLoading ? content.confirmButton.loading : content.confirmButton.initial }}
      </UiButton>
    </div>
    <div class="flex flex-col items-center">
      <p class="text-lg text-text-secondary">
        {{ content.createAccount.text }}
        <button 
          type="button" 
          @click="$emit('switch-to-register')"
          class="pl-2 text-primary font-bold hover:text-primary-hover"
        >
          {{ content.createAccount.button }}
        </button>
      </p>
    </div>
    <p v-if="formError" class="mt-4 text-center text-lg text-error">
      {{ formError }}
    </p>
  </form>
</template>

<style scoped lang="scss">

</style>
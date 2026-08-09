<script setup lang="ts">
  import { mapAuthPage } from '~/mappers/authPage';

  type AuthPageMapped = ReturnType<typeof mapAuthPage>;

  // --- Props & Emits ---
  const props = defineProps<{
    email: string
    content: AuthPageMapped['verify']
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
      fieldError.value = props.content.errors.verifyEmpty;
      return;
    }

    try {
      await auth.verifyEmail({
        email: props.email,
        code: code.value,
      });

      notifications.success(
        props.content.notifications.success.title,
        props.content.notifications.success.text,
      );
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
      notifications.success(
        props.content.notifications.send.title,
        props.content.notifications.send.text,
      )
    } catch (e) {
      const status = (e as any)?.status ?? (e as any)?.response?.status;
      const detail = (e as any)?.data?.detail;

      if (status === 429 && detail?.retry_after) {
        start(detail.retry_after);
        formError.value = detail.message ?? props.content.errors.resend;
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
        {{ content.title }}
      </h2>
      <p class="text-lg text-text-main">
        {{ content.text }} <span class="font-semibold">{{ email }}</span>
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
        <Icon name="fluent:arrow-sync-12-regular" mode="svg" class="w-full h-full" :class="{ 'animate-spin': auth.isLoading }"/>
      </UiButton>

      <p v-if="isCooldownActive" class="text-center text-lg text-text-main">
        {{ content.verifyResend.firstText.main }}
        <span>{{ secondsLeft }}</span>
        {{ content.verifyResend.firstText.time }}
      </p>
      <p v-else class="text-center text-lg text-text-main">
        {{ content.verifyResend.secondText.main }}
      </p>
    </div>

    <div class="grid grid-cols-2 gap-4 mb-4">
      <UiButton
        type="button"
        style-type="cancel"
        class="!py-3 !text-body-xl"
        @click="onCancel"
      >
        {{ content.cancelButton }}
      </UiButton>
      <UiButton
        type="submit"
        class="!py-3 !text-body-xl"
        :disabled="isConfirmDisabled"
      >
        {{ auth.isLoading ? content.confirmButton.loading : content.confirmButton.initial }}
      </UiButton>
    </div>
    
    <p v-if="formError" class="mt-4 text-center text-lg text-error">
      {{ formError }}
    </p>
  </form>
</template>

<style scoped lang="scss">

</style>
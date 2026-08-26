<script setup lang="ts">
  import { mapAuthPage } from '~/mappers/pages/authPage';

  type AuthPageMapped = ReturnType<typeof mapAuthPage>;

  const auth = useAuthStore()
  const emit = defineEmits<{
    'switch-to-login': []
    'switch-to-verify': [email: string]
  }>();
  const { detectedTimezone, timezoneOptions } = useTimezoneOptions();
  
  const props = defineProps<{
    content: AuthPageMapped['registration']
  }>();
  

  const username = ref('');
  const email = ref('');
  const password = ref('');
  const timezone = ref(detectedTimezone);

  const fieldErrors = ref({ 
    username: '',
    email: '', 
    password: '',
    timezone: '',
  });
  const formError = ref('');
  const isLoading = ref(false);

  const notifications = useNotificationsStore();

  async function onSubmit() {
    fieldErrors.value = { username: '', email: '', password: '', timezone: '' };
    formError.value = '';

    if (username.value.length < 3) fieldErrors.value.username = props.content.errors.nameValue;
    if (!email.value) fieldErrors.value.email = props.content.errors.emailEmpty;
    if (password.value.length < 8) fieldErrors.value.password = props.content.errors.passwordValue;
    if (!timezone.value) fieldErrors.value.timezone = props.content.errors.timezoneEmpty;

    if (Object.values(fieldErrors.value).some(Boolean)) return;

    try {
      await auth.register({ 
        username: username.value, 
        email: email.value, 
        password: password.value,
        timezone: timezone.value,
      });

      notifications.success(
        props.content.notifications.success.title,
        props.content.notifications.success.text.replace('{email}', email.value),
      );

      emit('switch-to-verify', email.value);
    } catch (e) {
      const parsed = parseApiError(e);
      fieldErrors.value = { ...fieldErrors.value, ...parsed.fieldErrors };
      formError.value = parsed.formError;

      if (parsed.formError) {
        notifications.error(
          props.content.notifications.error.title,
          parsed.formError
        )
      };
    };
  };

</script>

<template>
  <form @submit.prevent="onSubmit">
    <div class="mb-8 max-sm:mb-5">
      <h2 class="text-heading-lg font-bold text-text-main max-sm:text-3xl">
        {{ content.title }}
      </h2>
    </div>
    <div class="flex flex-col gap-4 mb-8">
      <UiInput 
        v-model="username"
        type="text"
        :placeholder="content.namePlaceholder"
        :error-message="fieldErrors.username"
        input-class="!bg-secondary"
      />
      <UiSelect
        v-model="timezone"
        :options="timezoneOptions"
        :placeholder="content.timezonePlaceholder"
        :error-message="fieldErrors.timezone"
        list-layout="bottom"
        button-style="!bg-secondary !border-0 !min-h-[61px] max-sm:!min-h-[58px]"
        list-style="!bg-secondary !border-0"
        list-button-style="!min-h-[61px] max-sm:!min-h-[58px]"

        search-style="!min-h-[61px] max-sm:!min-h-[58px]"
        search-visible
        search-placeholder="Search timezone..."
      />
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
    <div class="grid grid-cols-2 gap-4 mb-2 max-sm:grid-cols-1 max-sm:gap-2">
      <UiButton
        @click="$emit('switch-to-login')" 
        type="button"
        style-type="cancel"
        class="!py-3 !text-body-xl">
        {{ content.cancelButton }}
      </UiButton>
      <UiButton
        type="submit"
        :disabled="auth.isLoading"
        class="!py-3 !text-body-xl"
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
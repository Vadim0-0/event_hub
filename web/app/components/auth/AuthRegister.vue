<script setup lang="ts">

  const auth = useAuthStore()
  const emit = defineEmits<{ 'switch-to-login': [] }>()

  const username = ref('')
  const email = ref('')
  const password = ref('')

  const fieldErrors = ref({ username: '', email: '', password: '' })
  const formError = ref('')
  const isLoading = ref(false)

  const notifications = useNotificationsStore()

  async function onSubmit() {
    fieldErrors.value = { username: '', email: '', password: '' }
    formError.value = ''

    if (username.value.length < 3) fieldErrors.value.username = 'At least 3 characters'
    if (!email.value) fieldErrors.value.email = 'Enter your email address'
    if (password.value.length < 8) fieldErrors.value.password = 'At least 8 characters'
    if (Object.values(fieldErrors.value).some(Boolean)) return

    if (Object.values(fieldErrors.value).some(Boolean)) return
    try {
      await auth.register({ username: username.value, email: email.value, password: password.value });

      notifications.success(
        'Registration was successful',
        `The user ${email.value} has been successfully registered`,
      );

      emit('switch-to-login');
    } catch (e) {
      const parsed = parseApiError(e);
      fieldErrors.value = { ...fieldErrors.value, ...parsed.fieldErrors };
      formError.value = parsed.formError;

      if (parsed.formError) {
        notifications.error('Registration Error', parsed.formError)
      }
    }
  }

</script>

<template>
  <form @submit.prevent="onSubmit">
    <div class="flex flex-col gap-4 mb-8">
      <UiInput 
        v-model="username"
        type="text"
        placeholder="Name"
        :error-message="fieldErrors.username"  
      />
      <UiInput 
        v-model="email"
        type="email"
        placeholder="Login" 
        :error-message="fieldErrors.email"  
      />
      <UiInput 
        v-model="password"
        type="password"
        placeholder="Password" 
        :error-message="fieldErrors.password" 
      />
    </div>
    <div class="grid grid-cols-2 gap-4 mb-2">
      <button
        type="submit"
        :disabled="auth.isLoading"
        class="btn-global py-3">
        Register
      </button>
      <button
        @click="$emit('switch-to-login')" 
        type="button"
        class="btn-global py-3">
        Cancel
      </button>
    </div>
    <p v-if="formError" class="mt-4 text-center text-sm text-error">
      {{ formError }}
    </p>
  </form>
</template>

<style scoped lang="scss">

</style>
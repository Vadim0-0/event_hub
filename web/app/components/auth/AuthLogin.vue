<script setup lang="ts">

  const emit = defineEmits<{
    'switch-to-register': []
    'switch-to-verify': [email: string]
  }>();

  const auth = useAuthStore();
  const email = ref('');
  const password = ref('');
  const fieldErrors = ref({ email: '', password: '' });
  const formError = ref('');

  async function onSubmit() {
    fieldErrors.value = { email: '', password: '' }
    formError.value = ''

    if (!email.value) fieldErrors.value.email = 'Enter your email address'
    if (!password.value) fieldErrors.value.password = 'Enter your password'
    if (fieldErrors.value.email || fieldErrors.value.password) return

    try {
      await auth.login({ email: email.value, password: password.value })
    } catch (e: any) {
      formError.value = e.data?.detail || 'Login error'

      const status = (e as any)?.status ?? (e as any)?.response?.status;

      const detail = (e as any)?.data?.detail;
      if (status === 403 && detail === 'Email is not verified') {
        emit('switch-to-verify', email.value);
        return;
      };
    };
  };

</script>

<template>
  <form @submit.prevent="onSubmit">
    <div class="mb-8">
      <h2 class="text-heading-lg font-bold text-text-main">
        Login
      </h2>
    </div>
    <div class="flex flex-col gap-4 mb-6">
      <UiInput 
        v-model="email"
        type="email"
        placeholder="Login"
        :error-message="fieldErrors.email" 
        input-class="!bg-secondary"
      />
      <UiInput 
        v-model="password"
        type="password"
        placeholder="Password"
        :error-message="fieldErrors.password"
        input-class="!bg-secondary"
      />
    </div>
    <div class="grid grid-cols-2 gap-4 mb-6">
      <NuxtLink to="/" 
        class="
          btn-global py-3 
          
          bg-fourth text-text-main border-1 border-solid border-fifth
          hover:bg-third
        "
      >
        Cancel
      </NuxtLink>
      <UiButton
        type="submit"
        :disabled="auth.isLoading"
        class="!py-3 !text-body-xl"
      >
        Login
      </UiButton>
    </div>
    <div class="flex flex-col items-center">
      <p class="text-lg text-text-secondary">
        Don't have an account? 
        <button 
          type="button" 
          @click="$emit('switch-to-register')"
          class="pl-2 text-primary font-bold hover:text-primary-hover"
        
          >Sign Up</button>
      </p>
    </div>
    <p v-if="formError" class="mt-4 text-center text-lg text-error">
      {{ formError }}
    </p>
  </form>
</template>

<style scoped lang="scss">

</style>
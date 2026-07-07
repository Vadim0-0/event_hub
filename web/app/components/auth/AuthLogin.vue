<script setup lang="ts">

  const auth = useAuthStore()
  const email = ref('')
  const password = ref('')
  const fieldErrors = ref({ email: '', password: '' })
  const formError = ref('')

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
    }
  }

</script>

<template>
  <form @submit.prevent="onSubmit">
    <div class="flex flex-col gap-4 mb-8">
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
        Login
      </button>
      <NuxtLink to="/" class="btn-global py-3">
        Cancel
      </NuxtLink>
    </div>
    <div class="flex justify-center w-full">
      <button 
        @click="$emit('switch-to-register')"
        type="button" 
        class="
          btn-global w-full border-[2px] border-solid border-primary bg-transparent text-primary
          hover:bg-transparent hover:text-primary-hover hover:border-primary-hover
        "
      >
        Register
      </button>
    </div>
    <p v-if="formError" class="mt-4 text-center text-sm text-error">
      {{ formError }}
    </p>
  </form>
</template>

<style scoped lang="scss">

</style>
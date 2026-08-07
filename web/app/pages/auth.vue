<script setup lang="ts">
  definePageMeta({
    layout: 'auth',
    guestOnly: true,
  })

  useHead({
    title: 'Auth',
  });

  const mode = ref<'login' | 'register' | 'verify'>('login');
  const pendingEmail = ref('');

  function openVerify(email: string) {
    pendingEmail.value = email;
    mode.value = 'verify';
  };

  function backToLogin() {
    mode.value = 'login';
    pendingEmail.value = '';
  };

</script>

<template>
  <div class="flex flex-1">
    <div class="container mx-auto px-4 flex flex-1 items-center justify-center">
      <div class="w-full max-w-4xl p-5 rounded-2xl bg-primary-light ">
        <AuthLogin
          v-if="mode === 'login'"
          @switch-to-register="mode = 'register'"
          @switch-to-verify="openVerify"
        />
        <AuthRegister 
          v-else-if="mode === 'register'"
          @switch-to-login="backToLogin"
          @switch-to-verify="openVerify"
        />
        <AuthVerify 
          v-else-if="mode === 'verify'"
          :email="pendingEmail"
          @switch-to-login="backToLogin"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
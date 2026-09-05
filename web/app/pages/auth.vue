<script setup lang="ts">
  import authPageRaw from '~~/data/pages/authPage.json';
  import { mapAuthPage } from '~/mappers/pages/authPage';
  import type { AuthPageRaw } from '~/types/i18n/pages/authPage';

  const route = useRoute();
  const router = useRouter();

  const { showFor } = useLoader()

  type AuthMode = 'login' | 'register' | 'verify';

  definePageMeta({
    layout: 'auth',
    guestOnly: true,
  });

  const { content } = usePageContent(
    authPageRaw as AuthPageRaw[],
    mapAuthPage,
  );

  const mode = computed<AuthMode>({
    get() {
      const m = route.query.mode
      return m === 'register' || m === 'verify' ? m : 'login'
    },
    set(value) {
      router.replace({
        query: {
          ...route.query,
          mode: value === 'login' ? undefined : value,
          email: value === 'verify' ? pendingEmail.value || route.query.email : undefined,
        },
      })
    },
  });
  
  const pendingEmail = computed({
    get: () => String(route.query.email ?? ''),
    set: (email: string) => {
      router.replace({
        query: {
          ...route.query,
          email: email || undefined,
        },
      })
    },
  });

  async function switchToRegister() {
    await showFor(300);
    mode.value = 'register';
  };

  async function openVerify(email: string) {
    await showFor(300);
    pendingEmail.value = email;
    mode.value = 'verify';
  };

  async function backToLogin() {
    await showFor(300);
    mode.value = 'login';
  };

</script>

<template>
  <div class="flex flex-1">
    <div class="container mx-auto px-4 flex flex-1 items-center justify-center">
      <div class="w-full max-w-4xl p-5 rounded-2xl bg-primary-light ">
        <AuthLogin
          v-if="mode === 'login'"
          :content="content.login"
          @switch-to-register="switchToRegister"
          @switch-to-verify="openVerify"
        />
        <AuthRegister 
          v-else-if="mode === 'register'"
          :content="content.registration"
          @switch-to-login="backToLogin"
          @switch-to-verify="openVerify"
        />
        <AuthVerify 
          v-else-if="mode === 'verify'"
          :email="pendingEmail"
          :content="content.verify"
          @switch-to-login="backToLogin"
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">

</style>
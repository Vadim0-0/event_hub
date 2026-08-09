<script setup lang="ts">
  import authPageRaw from '~~/data/pages/authPage.json';
  import { mapAuthPage } from '~/mappers/authPage';
  import type { AuthPageRaw } from '~/types/authPage';

  const route = useRoute();
  const router = useRouter();

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

  function openVerify(email: string) {
    router.replace({
      query: {
        ...route.query,
        mode: 'verify',
        email,
      },
    })
  };

  function backToLogin() {
    router.replace({
      query: {
        ...route.query,
        mode: undefined,
        email: undefined,
      },
    })
  };

</script>

<template>
  <div class="flex flex-1">
    <div class="container mx-auto px-4 flex flex-1 items-center justify-center">
      <div class="w-full max-w-4xl p-5 rounded-2xl bg-primary-light ">
        <AuthLogin
          v-if="mode === 'login'"
          :content="content.login"
          @switch-to-register="mode = 'register'"
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
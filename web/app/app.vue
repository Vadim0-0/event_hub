<script setup lang="ts">
  import { DEV_PREVIEW_NOTIFICATIONS, randomNotificationPayload } from '~/constants/devPreview';

  const notifications = useNotificationsStore();

  const auth = useAuthStore();

  const { isVisible: isLoaderVisible } = useLoader();

  usePageScrollLockWhen(isLoaderVisible, { mobileOnly: false });

  onMounted(() => {
    if (auth.isAuthenticated) {
      auth.fetchMe();
    };

    if (!import.meta.dev || !DEV_PREVIEW_NOTIFICATIONS) return;

    const count = 4;
    
    for (let i = 0; i < count; i++) {
      const { type, title, message } = randomNotificationPayload();
      notifications.push({ type, title, message });
    }
  });
</script>

<template>
  <VueLenis root :options="{ duration: 1.4, smoothWheel: true }" />
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>

  <LayoutNotifications />

  <Transition name="loader">
    <LayoutLoader v-if="isLoaderVisible" />
  </Transition>
</template>

<style scoped lang="scss">
  .loader-enter-active,
  .loader-leave-active {
    transition: opacity 0.3s ease-in-out;
  }

  .loader-enter-from,
  .loader-leave-to {
    opacity: 0;
  }
</style>

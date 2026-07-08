<script setup lang="ts">
  const auth = useAuthStore()
</script>

<template>
  <VueLenis root :options="{ duration: 1.4, smoothWheel: true }" />
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>

  <LayoutNotifications />

  <Transition name="loader">
    <LayoutLoader v-if="auth.isLoading"/>
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

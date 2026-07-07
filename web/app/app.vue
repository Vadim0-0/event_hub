<template>
  <VueLenis root :options="{ duration: 1.4, smoothWheel: true }" />
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>

  <LayoutNotifications />
</template>

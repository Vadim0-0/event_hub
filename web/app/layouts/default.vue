<script setup lang="ts">

  const isTopButtonVisible = ref(false)

  useLenis(({ scroll, limit }: { scroll: number; limit: number }) => {
    isTopButtonVisible.value = scroll + window.innerHeight >= limit + 100
  })

</script>

<template>
  <main class="flex flex-col flex-1">
    <slot />
  </main>
  
  <LayoutAppIndexFooter />

  <Transition name="top-button">
    <LayoutTopButton v-if="isTopButtonVisible" />
  </Transition>
</template>

<style>

  .top-button-leave-active,
  .top-button-enter-active {
    transition: opacity 0.3s ease-in-out,
  }
    
  .top-button-enter-from,
  .top-button-leave-to {
    opacity: 0;
  }

</style>
<script setup lang="ts">
  const lenis = useLenis();

  function scrollToTop() {
    lenis.value?.scrollTo(0, {
      duration: 4,
    })
  };
</script>

<template>
  <button 
    @click="scrollToTop"
    class="
      btn-global fixed bottom-10 right-10 flex items-center justify-center p-0 w-15 h-15 rounded-[50%] z-100
      max-md:bottom-5 max-md:right-5 max-md:w-10 max-md:h-10 
    "
  >
    <Icon 
      name="tabler:arrow-up" 
      class="
        bg-main size-9
        max-md:size-6
      "
    />
  </button>
</template>
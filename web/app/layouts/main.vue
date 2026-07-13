<script setup lang="ts">
  const headerRef = ref<{ el: HTMLElement | null } | null>(null);
  const marginLeftStyle = ref({ marginLeft: '0px' });
  let resizeObserver: ResizeObserver | null = null;

  const updateMarginLeft = () => {
    if (headerRef.value) {
      const width = headerRef.value?.el?.offsetWidth;
      marginLeftStyle.value = { marginLeft: `${width}px` };
    };
  };

  onMounted(() => {
    const el = headerRef.value?.el;
    if (el) {
      updateMarginLeft();
      resizeObserver = new ResizeObserver(updateMarginLeft);
      resizeObserver.observe(el);
    };
  });

  onUnmounted(() => {
    if (resizeObserver) {
      resizeObserver.disconnect();
    };
  });

</script>

<template>
  <LayoutAppMainHeader ref="headerRef"/>
  <main 
    class="flex flex-col flex-1 h-dvh"
    :style="marginLeftStyle"
  >
    <slot />
  </main>
</template>

<style>

</style>
<script setup lang="ts">
  // Margin Left based on the header width
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

  // Loading Data
  const eventsStore = useEventsStore();
  const notifications = useNotificationsStore();

  onMounted(async () => {
    try {
      await eventsStore.fetchStats()
    } catch (e) {
      const parsed = parseApiError(e)
      notifications.error(
        'Ошибка',
        parsed.formError || 'Не удалось загрузить события',
      )
    }
  });

  // Visible EventInfo 
  const selectedEventStore = useSelectedEventStore();

</script>

<template>
  <LayoutAppMainHeader ref="headerRef"/>
  <main 
    class="flex flex-col flex-1 h-dvh"
    :style="marginLeftStyle"
  >
    <slot />
  </main>
  <Transition name="slide">
    <LayoutEventInfo
      v-if="selectedEventStore.isOpen"
      :event="selectedEventStore.selectedEvent!"
      @close="selectedEventStore.close()"
    />
  </Transition>
</template>

<style scoped lang="scss">

  .slide-enter-active,
  .slide-leave-active {
    transition: opacity 0.3s ease-in-out, transform 0.3s ease-in-out;
  }
  .slide-enter-from,
  .slide-leave-to {
    opacity: 1;
    transform: translateX(100%);
  }

</style>
<script setup lang="ts">
  import type { EventDetail, Event as AppEvent } from '~/types/event';

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
  const eventSetupStore = useEventSetupStore();
  const editProfilerStore = useEditProfilerStore();

  function openEventSetupCreate() {
    selectedEventStore.close();
    eventSetupStore.openCreate();
  };

  function openEventSetupEdit(event: AppEvent) {
    selectedEventStore.close();
    eventSetupStore.openEdit(event);
  };

  function closeEventSetup() {
    eventSetupStore.close();
  };

  function onEventSaved() {
    eventSetupStore.close();
    useEventsListRefreshStore().request();
    eventsStore.fetchStats();
  };

  function onEventUpdated(event: EventDetail) {
    selectedEventStore.updateSelectedEvent({
      participants_count: event.participants_count,
    });
    useEventsListRefreshStore().request();
  };

  function onEventDeleted() {
    selectedEventStore.close()
    eventSetupStore.close()
    useEventsListRefreshStore().request()
    eventsStore.fetchStats()
  };

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
      @updated="onEventUpdated"
      @edit="openEventSetupEdit"
    />
  </Transition>

  <Transition name="slide">
    <LayoutEventSetup
      v-if="eventSetupStore.isOpen"
      :mode="eventSetupStore.mode"
      :event="eventSetupStore.event"
      @close="closeEventSetup"
      @saved="onEventSaved"
      @deleted="onEventDeleted"
    />
  </Transition>

  <Transition name="smooth-appearance">
    <LayoutEditProfiler 
      v-if="editProfilerStore.isOpen"
      @close="editProfilerStore.close()"
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

  .smooth-appearance-enter-active,
  .smooth-appearance-leave-active {
    transition: opacity 0.3s ease-in-out;
  }
  .smooth-appearance-enter-from,
  .smooth-appearance-leave-to {
    opacity: 0;
  }

</style>
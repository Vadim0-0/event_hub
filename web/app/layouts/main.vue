<script setup lang="ts">
  import type { EventDetail, Event as AppEvent } from '~/types/domain/event';


  // --- Composables ---
  const eventsStore = useEventsStore();
  const notifications = useNotificationsStore();
  const selectedEventStore = useSelectedEventStore();
  const eventSetupStore = useEventSetupStore();
  const editProfilerStore = useEditProfilerStore();
  const messagingStore = useMessagingStore();
  const authStore = useAuthStore();
  const { onEvent } = useRealtime();
  const confirmStore = useConfirmStore();
  const aiChatStore = useAiChatStore();


  // --- Layout ---
  const headerRef = ref<{ el: HTMLElement | null } | null>(null);
  const marginLeftStyle = ref({ marginLeft: '0px' });
  const mapStore = useMapStore();

  let resizeObserver: ResizeObserver | null = null;

  function updateMarginLeft() {
    if (!headerRef.value?.el) return;
    marginLeftStyle.value = { marginLeft: `${headerRef.value.el.offsetWidth}px` };
  };


  // --- Event panels ---
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
    selectedEventStore.close();
    eventSetupStore.close();
    useEventsListRefreshStore().request();
    eventsStore.fetchStats();
  };

  
  // --- Realtime ---
  let unsubscribeRealtime: (() => void) | undefined;

  function handleRealtimeEvent(event: { type: string; payload: any }) {
    if (event.type === 'message.new') {
      const { conversation_id, message, sender_username } = event.payload;

      messagingStore.handleNewMessage(event.payload);

      if (message.sender_id === authStore.user?.id) return;
      if (messagingStore.activeConversationId === conversation_id) return;

      notifications.info(sender_username ?? 'New message', message.body);
      return;
    }

    if (event.type === 'conversation.cleared') {
      messagingStore.handleConversationCleared(event.payload);
      return;
    }

    if (event.type === 'conversation.deleted') {
      messagingStore.handleConversationDeleted(event.payload);
      return;
    }

    if (event.type === 'unread.updated') {
      messagingStore.setUnreadTotal(event.payload.total);
    }
  };


  // --- Lifecycle ---
  onMounted(async () => {
    const el = headerRef.value?.el;
    if (el) {
      updateMarginLeft();
      resizeObserver = new ResizeObserver(updateMarginLeft);
      resizeObserver.observe(el);
    }

    unsubscribeRealtime = onEvent(handleRealtimeEvent);

    try {
      await eventsStore.fetchStats();
    } catch (e) {
      const parsed = parseApiError(e);
      notifications.error(
        'Error',
        parsed.formError || 'Unable to load events',
      );
    }
  });

  onUnmounted(() => {
    resizeObserver?.disconnect();
    unsubscribeRealtime?.();
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

  <Transition name="smooth-appearance">
    <LayoutConfirm v-if="confirmStore.isOpen" />
  </Transition>

  <ClientOnly>
    <Transition name="smooth-appearance">
      <LayoutMap
        v-if="mapStore.isOpen"
        :latitude="mapStore.draft?.latitude ?? null"
        :longitude="mapStore.draft?.longitude ?? null"
        @update="mapStore.updateDraft"
        @confirm="mapStore.confirm"
        @cancel="mapStore.cancel"
      />
    </Transition>
  </ClientOnly>

  <LayoutAiChat v-if="aiChatStore.isOpen" />
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
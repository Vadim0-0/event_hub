import { defineStore } from 'pinia';
import type { Event } from '~/types/domain/event';

export const useSelectedEventStore = defineStore('selectedEvent', () => {
  const selectedEvent = ref<Event | null>(null);

  const isOpen = computed(() => selectedEvent.value !== null);

  function open(event: Event) {
    useEventSetupStore().close();
    selectedEvent.value = event;
  };

  function close() {
    selectedEvent.value = null
  };

  function isSelected(eventId: string) {
    return selectedEvent.value?.id === eventId
  };

  function updateSelectedEvent(data: Partial<Event>) {
    if (selectedEvent.value) {
      selectedEvent.value = { ...selectedEvent.value, ...data }
    };
  };

  return { 
    selectedEvent,
    isOpen,
    open,
    close,
    isSelected,
    updateSelectedEvent,
  };
});
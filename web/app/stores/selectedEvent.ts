import { defineStore } from 'pinia';
import type { Event } from '~/types/event';

export const useSelectedEventStore = defineStore('selectedEvent', () => {
  const selectedEvent = ref<Event | null>(null);

  const isOpen = computed(() => selectedEvent.value !== null);

  function open(event: Event) {
    selectedEvent.value = event
  };

  function close() {
    selectedEvent.value = null
  };

  function isSelected(eventId: string) {
    return selectedEvent.value?.id === eventId
  };

  return { 
    selectedEvent,
    isOpen,
    open,
    close,
    isSelected
  };
});
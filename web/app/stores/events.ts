import { defineStore } from 'pinia';

interface Event {
  id: number,
  title: string,
};

export const useEventsStore = defineStore('events', () => {
  const api = useApi();

  const createdEvents = ref<Event[]>([]);
  const joinedEvents = ref<Event[]>([]);
  const isLoading = ref(false);

  const createdCount = computed(() => createdEvents.value.length);
  const joinedCount = computed(() => joinedEvents.value.length);

  
});

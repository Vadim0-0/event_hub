import { defineStore } from 'pinia';

interface UserEventStats {
  created_count: number;
  joined_count: number;
};

let fetchPromise: Promise<void> | null = null;

export const useEventsStore = defineStore('events', () => {
  
  const api = useApi();

  const createdCount = ref(0);
  const joinedCount = ref(0);
  const isLoading = ref(false);

  async function fetchStats() {
    if (fetchPromise) return fetchPromise;

    fetchPromise = (async () => {
      isLoading.value = true;
  
      try {
        const stats = await api<UserEventStats>('/events/me/stats');
        createdCount.value = stats.created_count;
        joinedCount.value = stats.joined_count;
      } finally {
        isLoading.value = false;
      };
    })();

    try {
      await fetchPromise;
    } finally {
      fetchPromise = null;
    }
  };

  function reset() {
    createdCount.value = 0;
    joinedCount.value = 0;
  }

  return {
    createdCount,
    joinedCount,
    isLoading,
    fetchStats,
    reset
  };
});

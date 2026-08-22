export const useEventsListRefreshStore = defineStore('eventsListRefresh', () => {
  const tick = ref(0);
  function request() { tick.value++ };
  return { tick, request };
});
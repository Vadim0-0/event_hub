import { defineStore } from 'pinia';

export const useEditProfilerStore = defineStore('editProfiler', () => {
  const isOpen = ref(false);

  function open() {
    useSelectedEventStore().close();
    useEventSetupStore().close();

    isOpen.value = true;
  };

  function close() {
    isOpen.value = false;
  };

  return { 
    isOpen, 
    open, 
    close 
  };
})
import { defineStore } from 'pinia';
import type { Event } from '~/types/domain/event';

type EventSetupMode = 'create' | 'edit';

export const useEventSetupStore = defineStore('eventSetup', () => {
  const isOpen = ref(false);
  const mode = ref<EventSetupMode>('create');
  const event = ref<Event | null>(null);

  const isCreateMode = computed(() => mode.value === 'create');
  const isEditMode = computed(() => mode.value === 'edit');

  function openCreate() {
    mode.value = 'create';
    event.value = null;
    isOpen.value = true;
  };

  function openEdit(target: Event) {
    mode.value = 'edit';
    event.value = target;
    isOpen.value = true;
  };

  function close() {
    isOpen.value = false;
    event.value = null;
  };

  return {
    isOpen,
    mode,
    event,
    isCreateMode,
    isEditMode,
    openCreate,
    openEdit,
    close,
  };
});
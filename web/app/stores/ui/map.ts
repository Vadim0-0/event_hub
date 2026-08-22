import { defineStore } from 'pinia';

export type MapLocation = {
  location: string
  latitude: number
  longitude: number
};

type MapOpenOptions = {
  location?: string | null
  latitude?: number | null
  longitude?: number | null
  onConfirm: (value: MapLocation) => void
};

export const useMapStore = defineStore('map', () => {
  const isOpen = ref(false);
  const draft = ref<MapLocation | null>(null);
  const onConfirm = ref<((value: MapLocation) => void) | null>(null);

  function open(options: MapOpenOptions) {
    const hasCoords = options.latitude != null && options.longitude != null;

    draft.value = hasCoords
      ? {
          location: options.location ?? '',
          latitude: options.latitude!,
          longitude: options.longitude!,
        }
      : null;

    onConfirm.value = options.onConfirm;
    isOpen.value = true;
  }

  function updateDraft(value: MapLocation) {
    draft.value = value;
  }

  function confirm() {
    if (!draft.value || !onConfirm.value) return;
    onConfirm.value(draft.value);
    close();
  }

  function cancel() {
    close();
  }

  function close() {
    isOpen.value = false;
    draft.value = null;
    onConfirm.value = null;
  }

  return { 
    isOpen, 
    draft, 
    open, 
    updateDraft, 
    confirm, 
    cancel, 
    close 
  };
});
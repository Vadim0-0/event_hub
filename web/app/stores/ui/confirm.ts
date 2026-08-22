import { defineStore } from 'pinia';

export type ConfirmVariant = 'default' | 'delete';

export type ConfirmOptions = {
  variant?: ConfirmVariant; 
  title: string;
  description: string;
  confirmLabel: string;
  cancelLabel?: string;
  showCheckbox?: boolean;
  checkboxLabel?: string;
  onConfirm: (payload: { forEveryone?: boolean }) => void | Promise<void>;
};

export const useConfirmStore = defineStore('confirm', () => {
  const isOpen = ref(false);
  const options = ref<ConfirmOptions | null>(null);
  const checkboxValue = ref(false);
  const isLoading = ref(false);

  function open(next: ConfirmOptions) {
    options.value = next;
    checkboxValue.value = false;
    isLoading.value = false;
    isOpen.value = true;
  }

  function close() {
    isOpen.value = false;
    options.value = null;
    checkboxValue.value = false;
    isLoading.value = false;
  }

  async function confirm() {
    if (!options.value || isLoading.value) return;

    isLoading.value = true;
    try {
      await options.value.onConfirm({
        forEveryone: checkboxValue.value,
      });
      close();
    } finally {
      isLoading.value = false;
    }
  }

  return { 
    isOpen, 
    options, 
    checkboxValue, 
    isLoading, 
    open, 
    close, 
    confirm 
  };
});
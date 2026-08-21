type LaunchOrigin = {
  x: number
  y: number
  width: number
  height: number
};

function toLaunchOrigin(origin: DOMRect): LaunchOrigin {
  return {
    x: origin.x,
    y: origin.y,
    width: origin.width,
    height: origin.height,
  };
}

export const useAiChatStore = defineStore('aiChat', () => {
  const isOpen = ref(false);
  const launchOrigin = ref<LaunchOrigin | null>(null);
  const lastLaunchOrigin = ref<LaunchOrigin | null>(null);

  function open(origin?: DOMRect) {
    if (origin) {
      const nextOrigin = toLaunchOrigin(origin);
      launchOrigin.value = nextOrigin;
      lastLaunchOrigin.value = nextOrigin;
    }
    isOpen.value = true;
  }

  function close() {
    isOpen.value = false;
  }

  function clearLaunchOrigin() {
    launchOrigin.value = null;
  }

  return {
    isOpen,
    launchOrigin,
    lastLaunchOrigin,
    open,
    close,
    clearLaunchOrigin,
  };
});

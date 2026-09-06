const STORAGE_KEY = 'pwa-install-dismissed';

export function usePwaInstallPrompt() {
  const confirmStore = useConfirmStore();
  const nuxtApp = useNuxtApp();
  const isMobileViewport = useMediaQuery('(max-width: 767px)');

  let fallbackTimer: ReturnType<typeof setTimeout> | null = null;
  let primaryPromptShown = false;
  let installOfferSeen = false;

  function isStandalone() {
    return window.matchMedia('(display-mode: standalone)').matches
      || (window.navigator as Navigator & { standalone?: boolean }).standalone === true;
  }

  function isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent);
  }

  function isAndroid() {
    return /Android/i.test(navigator.userAgent);
  }

  function isMobileDevice() {
    return isMobileViewport.value || isAndroid() || isIOS();
  }

  function isInstalled() {
    return isStandalone() || unref(nuxtApp.$pwa?.isPWAInstalled) === true;
  }

  function wasDismissed() {
    return localStorage.getItem(STORAGE_KEY) === '1';
  }

  function markDismissed() {
    localStorage.setItem(STORAGE_KEY, '1');
  }

  function clearFallbackTimer() {
    if (fallbackTimer) {
      clearTimeout(fallbackTimer);
      fallbackTimer = null;
    }
  }

  function canShowPrompt() {
    if (!import.meta.client) return false;
    if (!isMobileDevice()) return false;
    if (isInstalled()) return false;
    if (wasDismissed()) return false;
    return true;
  }

  function openPrompt(options?: { manualAndroid?: boolean }) {
    if (!canShowPrompt() || confirmStore.isOpen) return;

    const ios = isIOS();
    const manualAndroid = options?.manualAndroid === true;

    if (!manualAndroid) {
      primaryPromptShown = true;
      clearFallbackTimer();
    }

    confirmStore.open({
      title: ios ? 'Добавить на экран' : 'Установить Event Hub?',
      description: ios
        ? 'Нажмите «Поделиться» в Safari, затем «На экран Домой».'
        : manualAndroid
          ? 'Откройте меню Chrome (⋮) → «Установить приложение» или «Добавить на главный экран».'
          : 'Добавьте приложение на главный экран для быстрого доступа.',
      confirmLabel: ios || manualAndroid ? 'Понятно' : 'Установить',
      cancelLabel: 'Не сейчас',
      showCheckbox: true,
      checkboxLabel: 'Больше не показывать',
      onConfirm: async () => {
        if (confirmStore.checkboxValue) {
          markDismissed();
        }

        if (!ios && !manualAndroid) {
          await nuxtApp.$pwa?.install();
          markDismissed();
          clearFallbackTimer();
        }
      },
    });
  }

  function tryShowPrompt() {
    if (!canShowPrompt()) return;

    if (nuxtApp.$pwa?.showInstallPrompt) {
      openPrompt();
      return;
    }

    if (isIOS()) {
      openPrompt();
    }
  }

  function tryShowAndroidFallback() {
    if (primaryPromptShown || installOfferSeen || wasDismissed() || isInstalled()) return;
    if (!canShowPrompt() || isIOS() || !isAndroid()) return;
    if (nuxtApp.$pwa?.showInstallPrompt) return;

    openPrompt({ manualAndroid: true });
  }

  watch(
    () => confirmStore.isOpen,
    (open, wasOpen) => {
      if (wasOpen && !open) {
        if (confirmStore.checkboxValue) {
          markDismissed();
        }
        clearFallbackTimer();
      }
    },
  );

  watch(
    () => nuxtApp.$pwa?.showInstallPrompt,
    (canInstall) => {
      if (canInstall) {
        installOfferSeen = true;
        tryShowPrompt();
      }
    },
    { immediate: true },
  );

  watch(
    () => unref(nuxtApp.$pwa?.isPWAInstalled),
    (installed) => {
      if (installed) {
        markDismissed();
        clearFallbackTimer();
      }
    },
  );

  function schedulePrompt() {
    clearFallbackTimer();

    setTimeout(() => {
      tryShowPrompt();
      fallbackTimer = setTimeout(tryShowAndroidFallback, 3000);
    }, 1500);
  }

  onUnmounted(clearFallbackTimer);

  return { schedulePrompt };
}

import pwaInstallPromptRaw from '~~/data/components/pwaInstallPrompt.json';
import { mapPwaInstallPrompt } from '~/mappers/components/pwaInstallPrompt';
import type { PwaInstallPromptRaw } from '~/types/i18n/components/pwaInstallPrompt';

const STORAGE_KEY = 'pwa-install-dismissed';

export function usePwaInstallPrompt() {
  const { locale } = useI18n();

  const confirmStore = useConfirmStore();
  const nuxtApp = useNuxtApp();
  const isMobileViewport = useMediaQuery('(max-width: 767px)');

  let fallbackTimer: ReturnType<typeof setTimeout> | null = null;
  let primaryPromptShown = false;
  let installOfferSeen = false;

  function isStandalone() {
    return window.matchMedia('(display-mode: standalone)').matches
      || (window.navigator as Navigator & { standalone?: boolean }).standalone === true;
  };

  function isIOS() {
    return /iPad|iPhone|iPod/.test(navigator.userAgent);
  };

  function isAndroid() {
    return /Android/i.test(navigator.userAgent);
  };

  function isMobileDevice() {
    return isMobileViewport.value || isAndroid() || isIOS();
  };

  function isInstalled() {
    return isStandalone() || unref(nuxtApp.$pwa?.isPWAInstalled) === true;
  };

  function wasDismissed() {
    return localStorage.getItem(STORAGE_KEY) === '1';
  };

  function markDismissed() {
    localStorage.setItem(STORAGE_KEY, '1');
  };

  function clearFallbackTimer() {
    if (fallbackTimer) {
      clearTimeout(fallbackTimer);
      fallbackTimer = null;
    };
  };

  function canShowPrompt() {
    if (!import.meta.client) return false;
    if (!isMobileDevice()) return false;
    if (isInstalled()) return false;
    if (wasDismissed()) return false;
    return true;
  };

  const content = computed(() =>
    mapPwaInstallPrompt((pwaInstallPromptRaw as PwaInstallPromptRaw[])[0]!, locale.value),
  );

  function openPrompt(options?: { manualAndroid?: boolean }) {
    if (!canShowPrompt() || confirmStore.isOpen) return;

    const ios = isIOS();
    const manualAndroid = options?.manualAndroid === true;

    if (!manualAndroid) {
      primaryPromptShown = true;
      clearFallbackTimer();
    };

    const t = content.value;

    confirmStore.open({
      title: ios ? t.iosTitle : t.androidTitle,
      description: ios
        ? t.iosDescription
        : manualAndroid
          ? t.androidManualDescription
          : t.androidDescription,
      confirmLabel: ios || manualAndroid ? t.confirmGotIt : t.confirmInstall,
      cancelLabel: t.cancelLabel,
      showCheckbox: true,
      checkboxLabel: t.checkboxLabel,
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
  };

  function tryShowPrompt() {
    if (!canShowPrompt()) return;

    if (nuxtApp.$pwa?.showInstallPrompt) {
      openPrompt();
      return;
    };

    if (isIOS()) {
      openPrompt();
    };
  };

  function tryShowAndroidFallback() {
    if (primaryPromptShown || installOfferSeen || wasDismissed() || isInstalled()) return;
    if (!canShowPrompt() || isIOS() || !isAndroid()) return;
    if (nuxtApp.$pwa?.showInstallPrompt) return;

    openPrompt({ manualAndroid: true });
  };

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
  };

  onUnmounted(clearFallbackTimer);

  return { schedulePrompt };
}

import pushNotificationPromptRaw from '~~/data/components/pushNotificationPrompt.json';
import { mapPushNotificationPrompt } from '~/mappers/components/pushNotificationPrompt';
import type { PushNotificationPromptRaw } from '~/types/i18n/components/pushNotificationPrompt';

function isIOSDevice() {
  if (!import.meta.client) return false;
  return /iPad|iPhone|iPod/.test(navigator.userAgent)
    || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
}

const STORAGE_KEY = 'push-notification-prompt-dismissed';

export function usePushNotificationPrompt() {
  const { locale } = useI18n();
  const confirmStore = useConfirmStore();
  const {
    availability,
    isSubscribed,
    refreshSubscriptionState,
    toggleFromUserGesture,
  } = usePushNotifications();

  let scheduleTimer: ReturnType<typeof setTimeout> | null = null;
  let retryTimer: ReturnType<typeof setTimeout> | null = null;
  let promptShown = false;
  let isPushPromptActive = false;

  const content = computed(() =>
    mapPushNotificationPrompt(
      (pushNotificationPromptRaw as PushNotificationPromptRaw[])[0]!,
      locale.value,
    ),
  );

  function wasDismissed() {
    return localStorage.getItem(STORAGE_KEY) === '1';
  };

  function markDismissed() {
    localStorage.setItem(STORAGE_KEY, '1');
  };

  function clearTimers() {
    if (scheduleTimer) {
      clearTimeout(scheduleTimer);
      scheduleTimer = null;
    };

    if (retryTimer) {
      clearTimeout(retryTimer);
      retryTimer = null;
    };
  };

  async function canShowPrompt() {
    if (!import.meta.client) return false;
    if (isIOSDevice()) return false;
    if (availability.value === 'unsupported') return false;
    if (availability.value === 'needs-pwa') return false;
    if (wasDismissed()) return false;
    if (confirmStore.isOpen) return false;
    if (Notification.permission === 'denied') return false;

    await refreshSubscriptionState();
    return !isSubscribed.value;
  };

  async function openPrompt() {
    if (promptShown || !(await canShowPrompt())) return;

    promptShown = true;
    isPushPromptActive = true;

    const t = content.value;

    confirmStore.open({
      title: t.title,
      description: t.description,
      confirmLabel: t.confirmLabel,
      cancelLabel: t.cancelLabel,
      showCheckbox: true,
      checkboxLabel: t.checkboxLabel,
      onConfirm: () => {
        if (confirmStore.checkboxValue) {
          markDismissed();
        }

        toggleFromUserGesture();
      },
    });
  };

  function scheduleRetry(delayMs = 800) {
    clearTimers();

    retryTimer = setTimeout(() => {
      void openPrompt();
    }, delayMs);
  };

  function schedulePrompt() {
    clearTimers();

    scheduleTimer = setTimeout(() => {
      void openPrompt();
    }, 2500);
  };

  watch(
    () => confirmStore.isOpen,
    (open, wasOpen) => {
      if (!wasOpen || open) return;

      if (isPushPromptActive) {
        isPushPromptActive = false;
        return;
      }

      if (promptShown || wasDismissed()) return;

      scheduleRetry();
    },
  );

  onUnmounted(clearTimers);

  return { schedulePrompt };
};

import pushNotificationsRaw from '~~/data/components/pushNotifications.json';
import { mapPushNotifications } from '~/mappers/components/pushNotifications';
import type { PushNotificationsRaw } from '~/types/i18n/components/pushNotifications';

export type PushAvailability = 'supported' | 'needs-pwa' | 'unsupported';

type VapidConfig = {
  public_key: string
  enabled: boolean
};

function urlBase64ToUint8Array(base64String: string) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }

  return outputArray;
}

export function isIOSDevice() {
  if (!import.meta.client) return false;
  return /iPad|iPhone|iPod/.test(navigator.userAgent)
    || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
}

function isStandalonePwa() {
  return window.matchMedia('(display-mode: standalone)').matches
    || (window.navigator as Navigator & { standalone?: boolean }).standalone === true;
}

function detectAvailability(): PushAvailability {
  if (!import.meta.client) return 'unsupported';
  if (!window.isSecureContext) return 'unsupported';
  if (!('serviceWorker' in navigator) || !('Notification' in window)) return 'unsupported';

  if (isIOSDevice() && !isStandalonePwa()) return 'needs-pwa';
  if (!('PushManager' in window)) return 'unsupported';

  return 'supported';
}

export function usePushNotifications() {
  const api = useApi();
  const notifications = useNotificationsStore();
  const { locale } = useI18n();

  const isSubscribed = ref(false);
  const isLoading = ref(false);
  const availability = ref<PushAvailability>('unsupported');
  const vapidConfig = ref<VapidConfig | null>(null);
  const swRegistration = ref<ServiceWorkerRegistration | null>(null);

  const isSupported = computed(() => availability.value === 'supported');
  const needsPwaInstall = computed(() => availability.value === 'needs-pwa');
  const notificationPermission = computed(() => {
    if (!import.meta.client || !('Notification' in window)) return 'unsupported';
    return Notification.permission;
  });

  const messages = computed(() =>
    mapPushNotifications((pushNotificationsRaw as PushNotificationsRaw[])[0]!, locale.value),
  );

  function refreshAvailability() {
    availability.value = detectAvailability();
  }

  async function prefetchVapidConfig() {
    if (availability.value !== 'supported') return;

    try {
      vapidConfig.value = await api<VapidConfig>('/push/vapid-public-key');
    } catch {
      vapidConfig.value = null;
    }
  }

  async function getVapidConfig() {
    if (vapidConfig.value) return vapidConfig.value;

    const config = await api<VapidConfig>('/push/vapid-public-key');
    vapidConfig.value = config;
    return config;
  }

  async function getServiceWorkerRegistration() {
    if (!('serviceWorker' in navigator)) return null;

    const existing = await navigator.serviceWorker.getRegistration();
    if (existing?.active) return existing;

    for (let attempt = 0; attempt < 10; attempt += 1) {
      const registration = await navigator.serviceWorker.getRegistration();
      if (registration?.active) return registration;
      await new Promise((resolve) => setTimeout(resolve, 300));
    }

    try {
      return await navigator.serviceWorker.ready;
    } catch {
      return null;
    }
  }

  async function preparePush() {
    refreshAvailability();
    if (availability.value !== 'supported') return;

    const [config, registration] = await Promise.all([
      prefetchVapidConfig(),
      getServiceWorkerRegistration(),
    ]);

    if (registration) swRegistration.value = registration;
    return { config: vapidConfig.value, registration: swRegistration.value };
  }

  function showPermissionDenied() {
    notifications.error(
      messages.value.deniedTitle,
      isIOSDevice() ? messages.value.deniedIosBody : messages.value.deniedBody,
    );
  }

  async function refreshSubscriptionState() {
    refreshAvailability();

    if (availability.value !== 'supported') {
      isSubscribed.value = false;
      return;
    }

    const registration = swRegistration.value ?? await getServiceWorkerRegistration();
    if (registration) swRegistration.value = registration;

    if (!registration) {
      isSubscribed.value = false;
      return;
    }

    const subscription = await registration.pushManager.getSubscription();
    isSubscribed.value = subscription !== null;
  }

  async function completeSubscribe(registration: ServiceWorkerRegistration) {
    const config = vapidConfig.value ?? await getVapidConfig();

    if (!config.enabled || !config.public_key) {
      notifications.error(messages.value.serverDisabledTitle, messages.value.serverDisabledBody);
      return false;
    }

    let subscription = await registration.pushManager.getSubscription();

    if (subscription) {
      await subscription.unsubscribe();
      subscription = null;
    }

    try {
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(config.public_key),
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Push subscription failed';
      const normalized = message.toLowerCase();

      if (normalized.includes('denied') || normalized.includes('not allowed')) {
        showPermissionDenied();
        return false;
      }

      notifications.error(messages.value.subscribeErrorTitle, message);
      return false;
    }

    const json = subscription.toJSON();
    const p256dh = json.keys?.p256dh;
    const auth = json.keys?.auth;

    if (!json.endpoint || !p256dh || !auth) {
      notifications.error(
        messages.value.subscribeErrorTitle,
        messages.value.missingSubscriptionKeys,
      );
      return false;
    }

    await api('/push/subscribe', {
      method: 'POST',
      body: {
        endpoint: json.endpoint,
        keys: { p256dh, auth },
        expirationTime: json.expirationTime ?? null,
      },
    });

    isSubscribed.value = true;
    notifications.success(messages.value.enabledTitle, messages.value.enabledBody);
    return true;
  }

  async function subscribe() {
    refreshAvailability();

    if (availability.value === 'needs-pwa') {
      notifications.info(messages.value.needsPwaTitle, messages.value.needsPwaBody);
      return false;
    }

    if (availability.value !== 'supported') {
      notifications.error(messages.value.disabledTitle, messages.value.disabledBody);
      return false;
    }

    if (Notification.permission !== 'granted') {
      showPermissionDenied();
      return false;
    }

    isLoading.value = true;

    try {
      const registration = swRegistration.value ?? await getServiceWorkerRegistration();
      if (!registration) {
        notifications.error(messages.value.swNotReadyTitle, messages.value.swNotReadyBody);
        return false;
      }

      swRegistration.value = registration;
      return await completeSubscribe(registration);
    } catch (error) {
      const parsed = parseApiError(error);
      notifications.error(
        messages.value.subscribeErrorTitle,
        parsed.formError || (error instanceof Error ? error.message : messages.value.unknownError),
      );
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  function toggleFromUserGesture() {
    if (isLoading.value) return;

    refreshAvailability();

    if (availability.value === 'needs-pwa') {
      notifications.info(messages.value.needsPwaTitle, messages.value.needsPwaBody);
      return;
    }

    if (isSubscribed.value) {
      void unsubscribe();
      return;
    }

    if (availability.value !== 'supported') {
      notifications.error(messages.value.disabledTitle, messages.value.disabledBody);
      return;
    }

    const runSubscribe = () => {
      isLoading.value = true;

      void (async () => {
        try {
          if (!swRegistration.value || !vapidConfig.value) {
            await preparePush();
          }

          const registration = swRegistration.value;
          if (!registration) {
            notifications.error(messages.value.swNotReadyTitle, messages.value.swNotReadyBody);
            return;
          }

          await completeSubscribe(registration);
        } catch (error) {
          const parsed = parseApiError(error);
          notifications.error(
            messages.value.subscribeErrorTitle,
            parsed.formError || (error instanceof Error ? error.message : messages.value.unknownError),
          );
        } finally {
          isLoading.value = false;
        }
      })();
    };

    if (Notification.permission === 'granted') {
      runSubscribe();
      return;
    }

    if (Notification.permission === 'denied') {
      showPermissionDenied();
      return;
    }

    Notification.requestPermission().then((permission) => {
      if (permission !== 'granted') {
        showPermissionDenied();
        return;
      }

      runSubscribe();
    });
  }

  async function unsubscribe() {
    if (availability.value !== 'supported') return;

    isLoading.value = true;

    try {
      const registration = swRegistration.value ?? await getServiceWorkerRegistration();
      const subscription = await registration?.pushManager.getSubscription();
      if (!subscription) {
        isSubscribed.value = false;
        return;
      }

      const endpoint = subscription.endpoint;

      await api('/push/subscribe', {
        method: 'DELETE',
        body: { endpoint },
      });

      await subscription.unsubscribe();
      isSubscribed.value = false;
    } finally {
      isLoading.value = false;
    }
  }

  async function toggle() {
    toggleFromUserGesture();
  }

  if (import.meta.client) {
    onMounted(() => {
      void preparePush();
      void refreshSubscriptionState();
    });
  }

  return {
    availability,
    isSupported,
    needsPwaInstall,
    notificationPermission,
    isSubscribed,
    isLoading,
    refreshAvailability,
    refreshSubscriptionState,
    subscribe,
    unsubscribe,
    toggle,
    toggleFromUserGesture,
  };
}

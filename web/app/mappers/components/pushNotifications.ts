import { pickScalar } from '~/composables/i18n/useLocalization';
import type { PushNotificationsRaw } from '~/types/i18n/components/pushNotifications';

export function mapPushNotifications(data: PushNotificationsRaw, locale: string) {
  return {
    needsPwaTitle: pickScalar(data.needsPwaTitle, locale),
    needsPwaBody: pickScalar(data.needsPwaBody, locale),
    disabledTitle: pickScalar(data.disabledTitle, locale),
    disabledBody: pickScalar(data.disabledBody, locale),
    deniedTitle: pickScalar(data.deniedTitle, locale),
    deniedBody: pickScalar(data.deniedBody, locale),
    deniedIosBody: pickScalar(data.deniedIosBody, locale),
    serverDisabledTitle: pickScalar(data.serverDisabledTitle, locale),
    serverDisabledBody: pickScalar(data.serverDisabledBody, locale),
    swNotReadyTitle: pickScalar(data.swNotReadyTitle, locale),
    swNotReadyBody: pickScalar(data.swNotReadyBody, locale),
    subscribeErrorTitle: pickScalar(data.subscribeErrorTitle, locale),
    missingSubscriptionKeys: pickScalar(data.missingSubscriptionKeys, locale),
    unknownError: pickScalar(data.unknownError, locale),
    enabledTitle: pickScalar(data.enabledTitle, locale),
    enabledBody: pickScalar(data.enabledBody, locale),
  };
}

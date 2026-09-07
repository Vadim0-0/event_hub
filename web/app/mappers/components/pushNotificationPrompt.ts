import { pickScalar } from '~/composables/i18n/useLocalization';
import type { PushNotificationPromptRaw } from '~/types/i18n/components/pushNotificationPrompt';

export function mapPushNotificationPrompt(data: PushNotificationPromptRaw, locale: string) {
  return {
    title: pickScalar(data.title, locale),
    description: pickScalar(data.description, locale),
    confirmLabel: pickScalar(data.confirmLabel, locale),
    cancelLabel: pickScalar(data.cancelLabel, locale),
    checkboxLabel: pickScalar(data.checkboxLabel, locale),
  };
}

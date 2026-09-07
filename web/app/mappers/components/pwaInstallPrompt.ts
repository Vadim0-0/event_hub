import { pickScalar } from '~/composables/i18n/useLocalization';
import type { PwaInstallPromptRaw } from '~/types/i18n/components/pwaInstallPrompt';

export function mapPwaInstallPrompt(data: PwaInstallPromptRaw, locale: string) {
  return {
    iosTitle: pickScalar(data.iosTitle, locale),
    androidTitle: pickScalar(data.androidTitle, locale),
    iosDescription: pickScalar(data.iosDescription, locale),
    androidDescription: pickScalar(data.androidDescription, locale),
    androidManualDescription: pickScalar(data.androidManualDescription, locale),
    confirmInstall: pickScalar(data.confirmInstall, locale),
    confirmGotIt: pickScalar(data.confirmGotIt, locale),
    cancelLabel: pickScalar(data.cancelLabel, locale),
    checkboxLabel: pickScalar(data.checkboxLabel, locale),
  };
};
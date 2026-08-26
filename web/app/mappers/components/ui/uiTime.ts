import { pickScalar } from '~/composables/i18n/useLocalization';
import type { UiTimeRaw } from '~/types/i18n/components/ui/uiTime';

export function mapUiTime(data: UiTimeRaw, locale: string) {
  return {
    timeFormatPlaceholder: pickScalar(data.timeFormatPlaceholder, locale),
    selectTimeTitle: pickScalar(data.selectTimeTitle, locale),
    amLabel: pickScalar(data.amLabel, locale),
    pmLabel: pickScalar(data.pmLabel, locale),
    cancelButton: pickScalar(data.cancelButton, locale),
    confirmButton: pickScalar(data.confirmButton, locale),
  };
}

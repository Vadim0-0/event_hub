import { pickArray, pickScalar } from '~/composables/i18n/useLocalization';
import type { UiDateRaw } from '~/types/i18n/components/ui/uiDate';

export function mapUiDate(data: UiDateRaw, locale: string) {
  return {
    dateFormatPlaceholder: pickScalar(data.dateFormatPlaceholder, locale),
    weekDays: pickArray(data.weekDays, locale),
    clearButton: pickScalar(data.clearButton, locale),
    todayButton: pickScalar(data.todayButton, locale),
    invalidDateFormat: pickScalar(data.invalidDateFormat, locale),
  };
}

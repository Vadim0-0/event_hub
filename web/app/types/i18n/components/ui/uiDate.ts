import type { LocalizedArray, LocalizedScalar } from '~/types/i18n/localizedPage';

export type UiDateRaw = {
  dateFormatPlaceholder: LocalizedScalar;
  weekDays: LocalizedArray;
  clearButton: LocalizedScalar;
  todayButton: LocalizedScalar;
  invalidDateFormat: LocalizedScalar;
};

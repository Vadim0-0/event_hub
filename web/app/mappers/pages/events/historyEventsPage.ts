import { pickScalar } from '~/composables/useLocalization';
import type { HistoryEventsPageRaw } from '~/types/i18n/pages/events/historyEventsPage';

export function mapHistoryEventsPage(data: HistoryEventsPageRaw, locale: string) {
  return {
    title: pickScalar(data.title, locale),
    infoText: pickScalar(data.infoText, locale),
    sortingButtonText: pickScalar(data.sortingButtonText, locale),
    loadingErrorText: pickScalar(data.loadingErrorText, locale),
    emptyText: pickScalar(data.emptyText, locale),
  }
};
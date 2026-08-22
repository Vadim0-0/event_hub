import { pickScalar } from '~/composables/i18n/useLocalization';
import type { MyEventsPageRaw } from '~/types/i18n/pages/events/myEventsPage';

export function mapMyEventsPage(data: MyEventsPageRaw, locale: string) {
  return {
    title: pickScalar(data.title, locale),
    infoText: pickScalar(data.infoText, locale),
    sortingButtonText: pickScalar(data.sortingButtonText, locale),
    loadingErrorText: pickScalar(data.loadingErrorText, locale),
    emptyText: pickScalar(data.emptyText, locale),
  }
};
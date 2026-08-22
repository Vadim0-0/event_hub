import { pickScalar } from '~/composables/i18n/useLocalization';
import type { AllEventsPageRaw } from '~/types/i18n/pages/events/allEventsPage';

export function mapAllEventsPage(data: AllEventsPageRaw, locale: string) {
  return {
    title: pickScalar(data.title, locale),
    infoText: pickScalar(data.infoText, locale),
    sortingButtonText: pickScalar(data.sortingButtonText, locale),
    loadingErrorText: pickScalar(data.loadingErrorText, locale),
    emptyText: pickScalar(data.emptyText, locale),
  }
};
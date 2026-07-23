import { pickScalar } from '~/composables/useLocalization';
import type { AllEventsPageRaw } from '~/types/allEventsPage';

export function mapAllEventsPage(data: AllEventsPageRaw, locale: string) {
  return {
    title: pickScalar(data.title, locale),
    infoText: pickScalar(data.infoText, locale),
    sortingButtonText: pickScalar(data.sortingButtonText, locale),
    loadingErrorText: pickScalar(data.loadingErrorText, locale),
    emptyText: pickScalar(data.emptyText, locale),
  }
};
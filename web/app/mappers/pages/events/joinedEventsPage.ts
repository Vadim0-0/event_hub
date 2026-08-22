import { pickScalar } from '~/composables/useLocalization';
import type { JoinedEventsPageRaw } from '~/types/i18n/pages/events/joinedEventsPage';

export function mapJoinedEventsPage(data: JoinedEventsPageRaw, locale: string) {
  return {
    title: pickScalar(data.title, locale),
    infoText: pickScalar(data.infoText, locale),
    sortingButtonText: pickScalar(data.sortingButtonText, locale),
    loadingErrorText: pickScalar(data.loadingErrorText, locale),
    emptyText: pickScalar(data.emptyText, locale),
  }
};
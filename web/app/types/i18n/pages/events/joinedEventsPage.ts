import type { LocalizedScalar } from '~/types/i18n/localizedPage';

export type JoinedEventsPageRaw = {
  title: LocalizedScalar
  infoText: LocalizedScalar
  sortingButtonText: LocalizedScalar
  loadingErrorText: LocalizedScalar
  emptyText: LocalizedScalar
};

export type JoinedEventsPageMapped = {
  title: string
  infoText: string
  sortingButtonText: string
  loadingErrorText: string
  emptyText: string
};
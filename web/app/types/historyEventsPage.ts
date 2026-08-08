import type { LocalizedScalar } from '~/types/localizedPage';

export type HistoryEventsPageRaw = {
  title: LocalizedScalar
  infoText: LocalizedScalar
  sortingButtonText: LocalizedScalar
  loadingErrorText: LocalizedScalar
  emptyText: LocalizedScalar
};

export type HistoryEventsPageMapped = {
  title: string
  infoText: string
  sortingButtonText: string
  loadingErrorText: string
  emptyText: string
};
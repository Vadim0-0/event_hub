import type { LocalizedScalar } from '~/types/localizedPage';

export type MyEventsPageRaw = {
  title: LocalizedScalar
  infoText: LocalizedScalar
  sortingButtonText: LocalizedScalar
  loadingErrorText: LocalizedScalar
  emptyText: LocalizedScalar
};

export type MyEventsPageMapped = {
  title: string
  infoText: string
  sortingButtonText: string
  loadingErrorText: string
  emptyText: string
};
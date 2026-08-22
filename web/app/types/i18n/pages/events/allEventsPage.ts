import type { LocalizedScalar } from '~/types/i18n/localizedPage';

export type AllEventsPageRaw = {
  title: LocalizedScalar
  infoText: LocalizedScalar
  sortingButtonText: LocalizedScalar
  loadingErrorText: LocalizedScalar
  emptyText: LocalizedScalar
};

export type AllEventsPageMapped = {
  title: string
  infoText: string
  sortingButtonText: string
  loadingErrorText: string
  emptyText: string
};
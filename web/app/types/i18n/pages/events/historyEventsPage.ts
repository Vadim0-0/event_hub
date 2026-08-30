import type { LocalizedScalar } from '~/types/i18n/localizedPage';
import type { LocalizedLoadMoreBtn, MappedLoadMoreBtn } from '~/types/i18n/pages/events/loadMoreBtn';

export type HistoryEventsPageRaw = {
  title: LocalizedScalar;
  infoText: LocalizedScalar;
  sortingButtonText: LocalizedScalar;
  loadingErrorText: LocalizedScalar;
  emptyText: LocalizedScalar;
  loadMoreBtn: LocalizedLoadMoreBtn;
};

export type HistoryEventsPageMapped = {
  title: string;
  infoText: string;
  sortingButtonText: string;
  loadingErrorText: string;
  emptyText: string;
  loadMoreBtn: MappedLoadMoreBtn;
};

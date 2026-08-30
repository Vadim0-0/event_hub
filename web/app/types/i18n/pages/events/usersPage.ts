import type { LocalizedScalar } from '~/types/i18n/localizedPage';
import type { LocalizedLoadMoreBtn, MappedLoadMoreBtn } from '~/types/i18n/pages/events/loadMoreBtn';

export type UsersPageRaw = {
  title: LocalizedScalar;
  infoText: LocalizedScalar;
  loadingErrorText: LocalizedScalar;
  emptyText: LocalizedScalar;
  loadMoreBtn: LocalizedLoadMoreBtn;
};

export type UsersPageMapped = {
  title: string;
  infoText: string;
  loadingErrorText: string;
  emptyText: string;
  loadMoreBtn: MappedLoadMoreBtn;
};

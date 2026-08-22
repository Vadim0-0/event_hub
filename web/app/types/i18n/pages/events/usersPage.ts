import type { LocalizedScalar } from '~/types/i18n/localizedPage';

export type UsersPageRaw = {
  title: LocalizedScalar
  infoText: LocalizedScalar
  loadingErrorText: LocalizedScalar
  emptyText: LocalizedScalar
};

export type UsersPageMapped = {
  title: string
  infoText: string
  loadingErrorText: string
  emptyText: string
};
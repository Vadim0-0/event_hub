import { pickScalar } from '~/composables/i18n/useLocalization';
import type { UsersPageRaw } from '~/types/i18n/pages/events/usersPage';

export function mapUsersPage(data: UsersPageRaw, locale: string) {
  return {
    title: pickScalar(data.title, locale),
    infoText: pickScalar(data.infoText, locale),
    loadingErrorText: pickScalar(data.loadingErrorText, locale),
    emptyText: pickScalar(data.emptyText, locale),
  }
};
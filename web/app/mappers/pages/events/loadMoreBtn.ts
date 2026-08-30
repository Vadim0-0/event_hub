import { pickScalar } from '~/composables/i18n/useLocalization';
import type { LocalizedLoadMoreBtn, MappedLoadMoreBtn } from '~/types/i18n/pages/events/loadMoreBtn';

export function mapLoadMoreBtn(data: LocalizedLoadMoreBtn, locale: string): MappedLoadMoreBtn {
  return {
    loadMore: pickScalar(data.loadMore, locale),
    loading: pickScalar(data.loading, locale),
  };
}

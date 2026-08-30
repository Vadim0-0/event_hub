import type { Event, EventsCount } from '~/types/domain/event';
import { useInfiniteList } from '~/composables/events/useInfiniteList';

const PAGE_SIZE = 30;
type SortOrder = 'asc' | 'desc';

export function useJoinedEventsList(
  enabled: Ref<boolean>,
  search: Ref<string> = ref(''),
  sort: Ref<SortOrder> = ref('asc'),
) {
  const api = useApi();

  const {
    items: events,
    total,
    totalPages,
    pending,
    isLoadingMore,
    hasMore,
    error,
    refresh,
    loadMore,
    pageSize,
  } = useInfiniteList<Event>({
    enabled,
    search,
    sort,
    pageSize: PAGE_SIZE,
    refreshOnStoreTick: true,
    fetchPage: (params) =>
      api<Event[]>(`/users/me/joined-events?${params.toString()}`),
    fetchCount: async (params) => {
      const suffix = params.toString() ? `?${params.toString()}` : '';
      const count = await api<EventsCount>(`/users/me/joined-events/count${suffix}`);
      return count.total;
    },
  });

  return {
    events,
    total,
    totalPages,
    pending,
    isLoadingMore,
    hasMore,
    error,
    refresh,
    loadMore,
    PAGE_SIZE: pageSize,
  };
}

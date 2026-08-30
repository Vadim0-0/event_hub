import type { Event, EventsCount } from '~/types/domain/event';
import { useInfiniteList } from '~/composables/events/useInfiniteList';

const PAGE_SIZE = 30;
type SortOrder = 'asc' | 'desc';

export function useHistoryEventsList(
  enabled: Ref<boolean> = ref(true),
  search: Ref<string> = ref(''),
  sort: Ref<SortOrder> = ref('desc'),
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
    fetchPage: (params) => api<Event[]>(`/events/history?${params.toString()}`),
    fetchCount: async (params) => {
      const suffix = params.toString() ? `?${params.toString()}` : '';
      const count = await api<EventsCount>(`/events/history/count${suffix}`);
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

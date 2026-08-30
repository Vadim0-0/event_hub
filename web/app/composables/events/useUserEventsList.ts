import type { Event, EventsCount } from '~/types/domain/event';
import { useInfiniteList } from '~/composables/events/useInfiniteList';

const PAGE_SIZE = 15;
type SortOrder = 'asc' | 'desc';

export function useUserEventsList(
  userId: Ref<number>,
  enabled: Ref<boolean>,
  sort: Ref<SortOrder> = ref('asc'),
  search: Ref<string> = ref(''),
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
    fetchPage: (params) => api<Event[]>(`/users/${userId.value}/events?${params.toString()}`),
    fetchCount: async (params) => {
      const suffix = params.toString() ? `?${params.toString()}` : '';
      const count = await api<EventsCount>(`/users/${userId.value}/events/count${suffix}`);
      return count.total;
    },
  });

  if (import.meta.client) {
    watch(userId, () => {
      if (enabled.value) void refresh();
    });
  }

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

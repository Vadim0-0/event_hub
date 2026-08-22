import type { Event, EventsCount } from '~/types/domain/event';

const PAGE_SIZE = 20;
type SortOrder = 'asc' | 'desc';

export function useHistoryEventsList(
  page: Ref<number>, 
  enabled: Ref<boolean> = ref(true),
  search: Ref<string> = ref(''),
  sort: Ref<SortOrder> = ref('desc'),
) {
  const api = useApi();
  const skip = computed(() => (page.value - 1) * PAGE_SIZE);
  const refreshStore = useEventsListRefreshStore();

  const queryParams = computed(() => {
    const params = new URLSearchParams({
      skip: String(skip.value),
      limit: String(PAGE_SIZE),
      sort: sort.value,
    })
    const trimmedSearch = search.value.trim()
    if (trimmedSearch) params.set('search', trimmedSearch)
    return params.toString()
  });

  const { data: events, pending, error, refresh } = useAsyncData(() => enabled.value
      ? `events-history-list-${page.value}-${search.value}-${sort.value}`
      : 'events-history-list-disabled', () => {
      if (!enabled.value) return Promise.resolve([] as Event[]);
      return api<Event[]>(`/events/history?${queryParams.value}`);
    },
    { watch: [page, search, sort, enabled], server: false },
  );

  const { data: countData } = useAsyncData(() => enabled.value
      ? `events-history-count-${search.value}`
      : 'events-history-count-disabled', () => {
      if (!enabled.value) return Promise.resolve({ total: 0 });
        
      const params = new URLSearchParams();
      const trimmedSearch = search.value.trim();
      if (trimmedSearch) params.set('search', trimmedSearch);

      const suffix = params.toString() ? `?${params.toString()}` : '';

      return api<EventsCount>(`/events/history/count${suffix}`);
    },
    { watch: [search, enabled], server: false },
  );

  const total = computed(() => countData.value?.total ?? 0);
  const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)));

  watch(() => refreshStore.tick, () => {
    if (enabled.value) refresh()
  });

  return {
    events,
    total,
    totalPages,
    pending,
    error,
    refresh,
    PAGE_SIZE,
  };
};

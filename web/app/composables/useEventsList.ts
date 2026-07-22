import type { Event, EventsCount } from '~/types/event';

const PAGE_SIZE = 20;
type SortOrder = 'asc' | 'desc';

export function useEventsList(
  page: Ref<number>, 
  enabled: Ref<boolean> = ref(true),
  search: Ref<string> = ref(''),
  sort: Ref<SortOrder> = ref('asc'),
) {
  const api = useApi();
  const skip = computed(() => (page.value - 1) * PAGE_SIZE);

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
      ? `events-list-${page.value}-${search.value}-${sort.value}`
      : 'events-list-disabled', () => {
      if (!enabled.value) return Promise.resolve([] as Event[]);
      return api<Event[]>(`/events/?${queryParams.value}`);
    },
    { watch: [page, search, sort, enabled], server: false },
  );

  const { data: countData } = useAsyncData(() => enabled.value
      ? `events-count-${search.value}`
      : 'events-count-disabled', () => {
      if (!enabled.value) return Promise.resolve({ total: 0 });
        
      const params = new URLSearchParams();
      const trimmedSearch = search.value.trim();
      if (trimmedSearch) params.set('search', trimmedSearch);

      const suffix = params.toString() ? `?${params.toString()}` : '';

      return api<EventsCount>(`/events/count${suffix}`);
    },
    { watch: [search, enabled], server: false },
  );

  const total = computed(() => countData.value?.total ?? 0);
  const totalPages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)));

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

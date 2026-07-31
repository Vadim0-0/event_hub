import type { Event, EventsCount } from '~/types/event';

const PAGE_SIZE = 20;
type SortOrder = 'asc' | 'desc';

export function useMyEventsList(
  page: Ref<number>,
  enabled: Ref<boolean>,
  search: Ref<string> = ref(''),
  sort: Ref<SortOrder> = ref('asc'),
) {
  const api = useApi();
  const refreshStore = useEventsListRefreshStore();
  const skip = computed(() => (page.value - 1) * PAGE_SIZE);

  const queryParams = computed(() => {
    const params = new URLSearchParams({
      skip: String(skip.value),
      limit: String(PAGE_SIZE),
      sort: sort.value,
    });
    const trimmedSearch = search.value.trim();
    if (trimmedSearch) params.set('search', trimmedSearch);
    return params.toString();
  });

  const { 
    data: events, 
    pending, 
    error, 
    refresh 
  } = useAsyncData(
    () => enabled.value
      ? `my-events-${page.value}-${search.value}-${sort.value}`
      : 'my-events-disabled',
    () => {
      if (!enabled.value) return Promise.resolve([] as Event[])
      return api<Event[]>(`/users/me/events?${queryParams.value}`)
    },
    { watch: [page, search, sort, enabled], server: false },
  );

  const { 
    data: countData, 
    refresh: refreshCount 
  } = useAsyncData(
    () => enabled.value
      ? `my-events-count-${search.value}`
      : 'my-events-count-disabled',
    () => {
      if (!enabled.value) return Promise.resolve({ total: 0 });

      const params = new URLSearchParams();
      const trimmedSearch = search.value.trim();
      if (trimmedSearch) params.set('search', trimmedSearch);

      const suffix = params.toString() ? `?${params.toString()}` : '';
      return api<EventsCount>(`/users/me/events/count${suffix}`);
    },
    { watch: [search, enabled], server: false },
  )

  const total = computed(() => countData.value?.total ?? 0);
  const totalPages = computed(() =>
    Math.max(1, Math.ceil(total.value / PAGE_SIZE)),
  )

  watch(() => refreshStore.tick, () => {
    if (!enabled.value) return
    refresh()
    refreshCount()
  });

  return { 
    events, 
    total, 
    totalPages, 
    pending, 
    error, 
    refresh, 
    PAGE_SIZE 
  };
}
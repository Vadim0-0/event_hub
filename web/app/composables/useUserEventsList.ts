import type { Event, EventsCount } from '~/types/domain/event';

const PAGE_SIZE = 15;
type SortOrder = 'asc' | 'desc';

export function useUserEventsList(
  userId: Ref<number>,
  enabled: Ref<boolean>,
  page: Ref<number>,
  sort: Ref<SortOrder> = ref('asc'),
  search: Ref<string> = ref(''),
) {
  const api = useApi();
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

  const { data: events, pending, error, refresh } = useAsyncData(
    () => enabled.value
      ? `user-events-${userId.value}-${page.value}-${sort.value}-${search.value}`
      : 'user-events-disabled',
    () => {
      if (!enabled.value) return Promise.resolve([] as Event[]);
      return api<Event[]>(`/users/${userId.value}/events?${queryParams.value}`);
    },
    { watch: [userId, page, sort, search, enabled], server: false },
  );

  const { data: countData } = useAsyncData(
    () => enabled.value
      ? `user-events-count-${userId.value}-${search.value}`
      : 'user-events-count-disabled',
    () => {
      if (!enabled.value) return Promise.resolve({ total: 0 });

      const params = new URLSearchParams();
      const trimmedSearch = search.value.trim();
      if (trimmedSearch) params.set('search', trimmedSearch);

      const suffix = params.toString() ? `?${params.toString()}` : '';
      return api<EventsCount>(`/users/${userId.value}/events/count${suffix}`);
    },
    { watch: [userId, search, enabled], server: false },
  );

  const total = computed(() => countData.value?.total ?? 0);
  const totalPages = computed(() =>
    Math.max(1, Math.ceil(total.value / PAGE_SIZE)),
  );

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
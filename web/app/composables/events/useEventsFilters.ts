type SortOrder = 'asc' | 'desc';

export function useEventsFilters() {
  const route = useRoute();
  const selectedEventStore = useSelectedEventStore();

  const search = ref(String(route.query.search ?? ''));
  const sort = ref<SortOrder>(route.query.sort === 'desc' ? 'desc' : 'asc');

  const debouncedSearch = ref(search.value);
  const applySearch = useDebounceFn((value: string) => {
    debouncedSearch.value = value
  }, 300);

  watch(search, (value) => applySearch(value));

  function buildQuery(pageValue: number) {
    return {
      ...(debouncedSearch.value ? { search: debouncedSearch.value } : {}),
      ...(sort.value !== 'asc' ? { sort: sort.value } : {}),
      ...(pageValue > 1 ? { page: pageValue } : {}),
    }
  };

  const page = computed({
    get: () => Number(route.query.page ?? 1),
    set: (value) => navigateTo({ path: route.path, query: buildQuery(value) }),
  });

  watch([debouncedSearch, sort], () => {
    selectedEventStore.close();
    if (page.value !== 1) page.value = 1;
  });

  function toggleSort() {
    sort.value = sort.value === 'asc' ? 'desc' : 'asc';
  };

  return {
    search,
    sort,
    debouncedSearch,
    page,
    toggleSort,
  };
}
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

  watch([debouncedSearch, sort], () => {
    selectedEventStore.close();
  });

  function toggleSort() {
    sort.value = sort.value === 'asc' ? 'desc' : 'asc';
  };

  return {
    search,
    sort,
    debouncedSearch,
    toggleSort,
  };
}
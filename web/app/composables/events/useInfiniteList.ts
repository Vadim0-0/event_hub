type SortOrder = 'asc' | 'desc';

type UseInfiniteListOptions<TItem extends { id: string | number }> = {
  enabled: Ref<boolean>;
  search: Ref<string>;
  sort?: Ref<SortOrder>;
  pageSize: number;
  fetchPage: (params: URLSearchParams) => Promise<TItem[]>;
  fetchCount: (params: URLSearchParams) => Promise<number>;
  appendBaseParams?: (params: URLSearchParams) => void;
  refreshOnStoreTick?: boolean;
};

export function useInfiniteList<TItem extends { id: string | number }>({
  enabled,
  search,
  sort,
  pageSize,
  fetchPage,
  fetchCount,
  appendBaseParams,
  refreshOnStoreTick = false,
}: UseInfiniteListOptions<TItem>) {
  const refreshStore = refreshOnStoreTick ? useEventsListRefreshStore() : null;

  const items = ref<TItem[]>([]) as Ref<TItem[]>;
  const total = ref(0);
  const pending = ref(false);
  const isLoadingMore = ref(false);
  const error = ref<unknown>(null);

  const hasMore = computed(() => items.value.length < total.value);
  const totalPages = computed(() =>
    Math.max(1, Math.ceil(total.value / pageSize)),
  );

  function buildCountParams() {
    const params = new URLSearchParams();
    const trimmedSearch = search.value.trim();
    if (trimmedSearch) params.set('search', trimmedSearch);
    appendBaseParams?.(params);
    return params;
  }

  function buildPageParams(skip: number) {
    const params = new URLSearchParams({
      skip: String(skip),
      limit: String(pageSize),
    });
    if (sort) params.set('sort', sort.value);
    const trimmedSearch = search.value.trim();
    if (trimmedSearch) params.set('search', trimmedSearch);
    appendBaseParams?.(params);
    return params;
  }

  async function fetchItems(reset = false) {
    if (!enabled.value) return;

    if (reset) {
      items.value = [];
      total.value = 0;
    }

    const skip = items.value.length;
    const isFirstPage = skip === 0;

    if (isFirstPage) pending.value = true;
    else isLoadingMore.value = true;

    try {
      const pageItems = await fetchPage(buildPageParams(skip));

      if (isFirstPage) {
        total.value = await fetchCount(buildCountParams());
      }

      const existingIds = new Set(items.value.map((item) => item.id));
      const unique = pageItems.filter((item) => !existingIds.has(item.id));

      items.value = reset ? pageItems : [...items.value, ...unique];
      error.value = null;
    } catch (e) {
      error.value = e;
    } finally {
      pending.value = false;
      isLoadingMore.value = false;
    }
  }

  async function refresh() {
    await fetchItems(true);
  }

  async function loadMore() {
    if (!enabled.value || pending.value || isLoadingMore.value || !hasMore.value) {
      return;
    }
    await fetchItems(false);
  }

  function syncList() {
    if (enabled.value) {
      void refresh();
    } else {
      items.value = [];
      total.value = 0;
      error.value = null;
    }
  }

  if (import.meta.client) {
    watch(
      sort ? [enabled, search, sort] : [enabled, search],
      syncList,
      { immediate: true },
    );

    if (refreshStore) {
      watch(() => refreshStore.tick, () => {
        if (enabled.value) void refresh();
      });
    }
  }

  return {
    items,
    total,
    totalPages,
    pending,
    isLoadingMore,
    hasMore,
    error,
    refresh,
    loadMore,
    pageSize,
  };
}

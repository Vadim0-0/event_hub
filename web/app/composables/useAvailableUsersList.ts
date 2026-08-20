import type { AvailableUsersListResponse } from '~/types/messaging';
import type { UserListItem } from '~/types/user';

const PAGE_SIZE = 30;

export function useAvailableUsersList(
  enabled: Ref<boolean>,
  search: Ref<string>,
) {
  const api = useApi();

  const users = ref<UserListItem[]>([]);
  const total = ref(0);
  const pending = ref(false);
  const isLoadingMore = ref(false);
  const error = ref<unknown>(null);

  const hasMore = computed(() => users.value.length < total.value);

  async function fetchUsers(reset = false) {
    if (!enabled.value) return;

    if (reset) {
      users.value = [];
      total.value = 0;
    }

    const skip = users.value.length;
    const isFirstPage = skip === 0;

    if (isFirstPage) pending.value = true;
    else isLoadingMore.value = true;

    try {
      const params = new URLSearchParams({
        skip: String(skip),
        limit: String(PAGE_SIZE),
      });

      const trimmed = search.value.trim();
      if (trimmed) params.set('search', trimmed);

      const data = await api<AvailableUsersListResponse>(
        `/conversations/available-users?${params.toString()}`,
      );

      const existingIds = new Set(users.value.map(u => u.id));
      const unique = data.items.filter(u => !existingIds.has(u.id));

      users.value = reset ? data.items : [...users.value, ...unique];
      total.value = data.total;
      error.value = null;
    } catch (e) {
      error.value = e;
      throw e;
    } finally {
      pending.value = false;
      isLoadingMore.value = false;
    }
  };

  async function refresh() {
    await fetchUsers(true);
  };

  async function loadMore() {
    if (!enabled.value || pending.value || isLoadingMore.value || !hasMore.value) {
      return;
    }
    await fetchUsers(false);
  };

  watch([enabled, search], () => {
    if (enabled.value) {
      void refresh();
    } else {
      users.value = [];
      total.value = 0;
    }
  });

  return {
    users,
    total,
    pending,
    isLoadingMore,
    hasMore,
    error,
    refresh,
    loadMore,
    PAGE_SIZE,
  };
};
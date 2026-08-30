import type { UserListItem, UsersCount } from '~/types/domain/user';
import { useInfiniteList } from '~/composables/events/useInfiniteList';

const PAGE_SIZE = 30;

export function useUsersList(
  enabled: Ref<boolean>,
  search: Ref<string> = ref(''),
) {
  const api = useApi();

  const {
    items: users,
    total,
    totalPages,
    pending,
    isLoadingMore,
    hasMore,
    error,
    refresh,
    loadMore,
    pageSize,
  } = useInfiniteList<UserListItem>({
    enabled,
    search,
    pageSize: PAGE_SIZE,
    appendBaseParams: (params) => {
      params.set('include_me', 'false');
    },
    fetchPage: (params) => api<UserListItem[]>(`/users/?${params.toString()}`),
    fetchCount: async (params) => {
      const suffix = params.toString() ? `?${params.toString()}` : '';
      const count = await api<UsersCount>(`/users/count${suffix}`);
      return count.total;
    },
  });

  return {
    users,
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

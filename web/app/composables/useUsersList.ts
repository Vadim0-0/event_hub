import type { UserListItem, UsersCount } from '~/types/user';

const PAGE_SIZE = 30;

export function useUsersList(
  page: Ref<number>,
  enabled: Ref<boolean>,
  search: Ref<string> = ref(''),
) {
  const api = useApi();
  const skip = computed(() => (page.value - 1) * PAGE_SIZE);

  const queryParams = computed(() => {
    const params = new URLSearchParams({
      skip: String(skip.value),
      limit: String(PAGE_SIZE),
      include_me: 'false',
    });
    const trimmedSearch = search.value.trim();
    if (trimmedSearch) params.set('search', trimmedSearch);
    return params.toString();
  });

  const { data: users, pending, error, refresh } = useAsyncData(
    () => enabled.value
      ? `users-list-${page.value}-${search.value}`
      : 'users-list-disabled',
    () => {
      if (!enabled.value) return Promise.resolve([] as UserListItem[]);
      return api<UserListItem[]>(`/users/?${queryParams.value}`);
    },
    { watch: [page, search, enabled], server: false },
  );

  const { data: countData, refresh: refreshCount } = useAsyncData(
    () => enabled.value
      ? `users-count-${search.value}`
      : 'users-count-disabled',
    () => {
      if (!enabled.value) return Promise.resolve({ total: 0 });

      const params = new URLSearchParams({ include_me: 'false' });
      const trimmedSearch = search.value.trim();
      if (trimmedSearch) params.set('search', trimmedSearch);

      const suffix = params.toString() ? `?${params.toString()}` : '';
      return api<UsersCount>(`/users/count${suffix}`);
    },
    { watch: [search, enabled], server: false },
  );

  const total = computed(() => countData.value?.total ?? 0);
  const totalPages = computed(() =>
    Math.max(1, Math.ceil(total.value / PAGE_SIZE)),
  );

  return { 
    users, 
    total, 
    totalPages, 
    pending, 
    error, 
    refresh, 
    PAGE_SIZE 
  };
}
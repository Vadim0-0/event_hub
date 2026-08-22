import type { ConversationsListResponse, Conversation } from '~/types/domain/messaging';

const PAGE_SIZE = 50;

export function useConversationsList(search: Ref<string>) {
  const api = useApi();

  const queryParams = computed(() => {
    const params = new URLSearchParams({
      skip: '0',
      limit: String(PAGE_SIZE),
    })
    const trimmed = search.value.trim()
    if (trimmed) params.set('search', trimmed)
    return params.toString()
  });

  const { data, pending, error, refresh } = useAsyncData(
    () => `conversations-list-${search.value}`,
    () => api<ConversationsListResponse>(`/conversations/?${queryParams.value}`),
    { watch: [search], server: false },
  );

  const conversations = computed<Conversation[]>(() => data.value?.items ?? []);
  const total = computed(() => data.value?.total ?? 0);

  return { 
    conversations, 
    total, 
    pending, 
    error, 
    refresh 
  };
}
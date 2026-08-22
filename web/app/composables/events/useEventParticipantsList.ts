import type { Participant } from '~/types/domain/event';

const PAGE_SIZE = 20;

export function useEventParticipantsList(
  eventId: Ref<string>,
  enabled: Ref<boolean>,
  page: Ref<number> = ref(1),
) {
  const api = useApi();
  const skip = computed(() => (page.value - 1) * PAGE_SIZE);

  const queryParams = computed(() =>
    new URLSearchParams({
      skip: String(skip.value),
      limit: String(PAGE_SIZE),
    }).toString(),
  );

  const { data: participants, pending, error, refresh } = useAsyncData(
    () => enabled.value
      ? `event-participants-${eventId.value}-${page.value}`
      : 'event-participants-disabled',
    () => {
      if (!enabled.value) return Promise.resolve([] as Participant[]);
      return api<Participant[]>(`/events/${eventId.value}/participants?${queryParams.value}`);
    },
    { watch: [eventId, page, enabled], server: false },
  );

  return {
    participants,
    pending,
    error,
    refresh,
    PAGE_SIZE,
  };
}
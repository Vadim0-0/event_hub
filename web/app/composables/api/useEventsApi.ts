import type { Event, EventDetail, Participant } from '~/types/domain/event';

export function useEventsApi() {
  const api = useApi();

  function getEventById(eventId: string) {
    return api<EventDetail>(`/events/${eventId}`);
  };

  function joinEvent(eventId: string) {
    return api(`/events/${eventId}/join`, { 
      method: 'POST' 
    });
  };

  function leaveEvent(eventId: string) {
    return api(`/events/${eventId}/leave`, { 
      method: 'DELETE' 
    });
  };

  function listParticipants(eventId: string, skip = 0, limit = 20) {
    const params = new URLSearchParams({
      skip: String(skip),
      limit: String(limit),
    });
    return api<Participant[]>(`/events/${eventId}/participants?${params}`);
  };

  function removeParticipant(eventId: string, userId: number) {
    return api(`/events/${eventId}/participants/${userId}`, {
      method: 'DELETE',
    });
  };

  return {
    getEventById,
    joinEvent,
    leaveEvent,
    listParticipants,
    removeParticipant,
  };
};
import type { Event } from '~/types/domain/event';
export type AiMessageRole = 'user' | 'assistant';

export type AiMessage = {
  id: string
  role: AiMessageRole
  body: string
  created_at: string
  pendingEventAction?: AiEventDraft | null
};

export type AiMessageOut = {
  id: string
  role: string
  content: string
  created_at: string
};

export type AiMessagesListOut = {
  items: AiMessageOut[]
  total: number
};

export type AiChatResponse = {
  reply: string
  model: string
  user_message_id: string
  assistant_message_id: string
  draft?: AiEventDraft | null
  ready_to_create?: boolean
};

export type AiHealthResponse = {
  enabled: boolean
  available: boolean
  model: string
};


export type AiEventDraft = {
  title: string
  description?: string | null
  starts_at: string
  location?: string | null
  latitude?: number | null
  longitude?: number | null
  max_participants?: number | null
};


export type AiEventDraftResponse = {
  reply: string
  draft: AiEventDraft | null
  ready_to_create: boolean
};


export type AiEventCreateResponse = {
  reply: string
  event: Event
};


export type AiPendingEventAction = {
  assistantMessageId: string
  draft: AiEventDraft
}
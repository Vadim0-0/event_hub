export type AiMessageRole = 'user' | 'assistant';

export type AiMessage = {
  id: string
  role: AiMessageRole
  body: string
  created_at: string
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
};

export type AiHealthResponse = {
  enabled: boolean
  available: boolean
  model: string
};
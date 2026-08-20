import type { UserListItem } from '~/types/user';

export type Message = {
  id: string
  conversation_id: string
  sender_id: number
  body: string
  created_at: string
  is_deleted: boolean
};

export type ConversationParticipant = {
  id: number
  username: string
};

export type Conversation = {
  id: string
  participant: ConversationParticipant
  last_message: Message | null
  unread_count: number
  updated_at: string
};

export type ConversationsListResponse = {
  items: Conversation[]
  total: number
};

export type MessageNewPayload = {
  conversation_id: string
  sender_username: string
  message: Message
};

export type ConversationActionPayload = {
  conversation_id: string
  for_everyone: boolean
};

export type AvailableUsersListResponse = {
  items: UserListItem[]
  total: number
};
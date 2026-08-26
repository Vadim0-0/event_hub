import type { LocalizedScalar } from '~/types/i18n/localizedPage';

export type ConversationChatRaw = {
  title: LocalizedScalar;
  loadingOlderMessages: LocalizedScalar;
  beginningOfConversation: LocalizedScalar;
  loadingMessages: LocalizedScalar;
  noMessages: LocalizedScalar;
  today: LocalizedScalar;
  yesterday: LocalizedScalar;
};

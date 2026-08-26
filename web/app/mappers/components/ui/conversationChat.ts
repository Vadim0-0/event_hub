import { pickScalar } from '~/composables/i18n/useLocalization';
import type { ConversationChatRaw } from '~/types/i18n/components/ui/conversationChat';

export function mapConversationChat(data: ConversationChatRaw, locale: string) {
  return {
    title: pickScalar(data.title, locale),
    loadingOlderMessages: pickScalar(data.loadingOlderMessages, locale),
    beginningOfConversation: pickScalar(data.beginningOfConversation, locale),
    loadingMessages: pickScalar(data.loadingMessages, locale),
    noMessages: pickScalar(data.noMessages, locale),
    today: pickScalar(data.today, locale),
    yesterday: pickScalar(data.yesterday, locale),
  };
}

import { pickScalar } from '~/composables/i18n/useLocalization';
import type { ChatsPageRaw } from '~/types/i18n/pages/chatsPage';

export function mapChatsPage(data: ChatsPageRaw, locale: string) {
  return {
    title: pickScalar(data.title, locale),
    searchPlaceholder: pickScalar(data.searchPlaceholder, locale),
    loading: pickScalar(data.loading, locale),
    emptyConversations: pickScalar(data.emptyConversations, locale),
    emptyUsers: pickScalar(data.emptyUsers, locale),
    startChatPreview: pickScalar(data.startChatPreview, locale),
    chatSubtitle: pickScalar(data.chatSubtitle, locale),
    messagePlaceholder: pickScalar(data.messagePlaceholder, locale),
    emptyState: pickScalar(data.emptyState, locale),
    confirmClearTitle: pickScalar(data.confirmClearTitle, locale),
    confirmClearDescription: pickScalar(data.confirmClearDescription, locale),
    confirmClearButton: pickScalar(data.confirmClearButton, locale),
    confirmClearForEveryone: pickScalar(data.confirmClearForEveryone, locale),
    confirmDeleteTitle: pickScalar(data.confirmDeleteTitle, locale),
    confirmDeleteDescription: pickScalar(data.confirmDeleteDescription, locale),
    confirmDeleteButton: pickScalar(data.confirmDeleteButton, locale),
    confirmDeleteForEveryone: pickScalar(data.confirmDeleteForEveryone, locale),
    errorTitle: pickScalar(data.errorTitle, locale),
    startChatError: pickScalar(data.startChatError, locale),
    clearChatError: pickScalar(data.clearChatError, locale),
    deleteChatError: pickScalar(data.deleteChatError, locale),
  };
}
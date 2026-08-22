import { pickScalar } from '~/composables/i18n/useLocalization';
import type { AiChatRaw } from '~/types/i18n/components/aiChat';

export function mapAiChat(data: AiChatRaw, locale: string) {
  return {
    title: pickScalar(data.title, locale),
    loadingOlderMessages: pickScalar(data.loadingOlderMessages, locale),
    beginningOfConversation: pickScalar(data.beginningOfConversation, locale),
    loadingMessages: pickScalar(data.loadingMessages, locale),
    aiUnavailable: pickScalar(data.aiUnavailable, locale),
    askSomething: pickScalar(data.askSomething, locale),
    cancelButton: pickScalar(data.cancelButton, locale),
    confirmButton: pickScalar(data.confirmButton, locale),
    typing: pickScalar(data.typing, locale),
  };
}
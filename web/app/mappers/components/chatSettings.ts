import { pickScalar } from '~/composables/i18n/useLocalization';
import type { ChatSettingsRaw } from '~/types/i18n/components/chatSettings';

export function mapChatSettings(data: ChatSettingsRaw, locale: string) {
  return {
    chatSettingsButton: data.chatSettingsButton.map((item) => ({
      icon: item.icon,
      type: item.type,
      isDelete: item.isDelete ?? false,
      text: pickScalar(item.text, locale),
    })),
  };
}
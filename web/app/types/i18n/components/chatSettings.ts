import type { LocalizedScalar } from '~/types/i18n/localizedPage';

export type ChatSettingsButtonType = 'clearHistory' | 'deleteChat';

export type ChatSettingsButtonRaw = {
  icon: string
  text: LocalizedScalar
  type: ChatSettingsButtonType
  isDelete?: boolean
};

export type ChatSettingsRaw = {
  chatSettingsButton: ChatSettingsButtonRaw[]
};
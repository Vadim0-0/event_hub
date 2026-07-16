import { pickScalar } from '~/composables/useLocalization';
import type { MainHeaderRaw } from '~/types/mainHeader';

export function mapMainHeader(data: MainHeaderRaw, locale: string) {
  return {
    statistics: data.statistics.map((item) => ({
      id: item.id,
      text: pickScalar(item.text, locale),
      icon: item.icon,
      countKey: item.countKey,
    })),
    profileBtns: data.profileBtns.map((item) => ({
      id: item.id,
      text: pickScalar(item.text, locale),
      icon: item.icon,
    })),
    profileDefaults: {
      username: pickScalar(data.profileDefaults.username, locale),
      email: pickScalar(data.profileDefaults.email, locale),
    },
    navigation: data.navigation.map((item) => ({
      id: item.id,
      to: item.to,
      text: pickScalar(item.text, locale),
      icon: item.icon,
    }))
  }
};
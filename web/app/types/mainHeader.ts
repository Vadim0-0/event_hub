import type { LocalizedScalar } from '~/types/localizedPage';

export type StatisticCountKey = 'createdCount' | 'joinedCount';

// ============ RAW ============
export type MainHeaderRaw = {
  statistics: Array<{
    id: string
    text: LocalizedScalar
    icon: string
    countKey: StatisticCountKey
  }>
  profileBtns: Array<{
    id: string
    text: LocalizedScalar
    icon: string
  }>
  profileDefaults: {
    username: LocalizedScalar
    email: LocalizedScalar
  },
  navigation: Array<{
    id: string
    to: string
    text: LocalizedScalar
    icon: string
  }>
};

// ============ MAPPED ============
export type StatisticItem = {
  id: string
  text: string
  icon: string
  count: number
};

export type ProfileBtnItem = {
  id: string
  text: string
  icon: string
};

export type ProfileDefaults = {
  username: string
  email: string
};

export type NavigationItem = {
  id: string
  to: string
  text: string
  icon: string
};


export type HeaderProfileHoverProps = {
  statistics: StatisticItem[]
  profileBtns: ProfileBtnItem[]
  defaults: ProfileDefaults
};

export type HeaderNavigation = {
  navigation: NavigationItem[]
};
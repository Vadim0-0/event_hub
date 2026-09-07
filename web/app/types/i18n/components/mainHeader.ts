import type { LocalizedScalar } from '../localizedPage';

export type StatisticCountKey = 'createdCount' | 'joinedCount';

// ============ RAW ============
export type MainHeaderRaw = {
  statistics: Array<{
    id: string
    text: LocalizedScalar
    icon: string
    countKey: StatisticCountKey
  }>
  profileBtns: Array<
    | {
      id: string
      text: LocalizedScalar
      icon: string
    }
    | {
      id: string
      'text-on': LocalizedScalar
      'text-off': LocalizedScalar
      'text-needs-pwa'?: LocalizedScalar
      'icon-on': string
      'icon-off': string
    }
  >
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

export type ProfileBtnItem =
  | {
    id: string
    kind: 'action'
    text: string
    icon: string
  }
  | {
    id: string
    kind: 'toggle'
    textOn: string
    textOff: string
    textNeedsPwa?: string
    iconOn: string
    iconOff: string
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
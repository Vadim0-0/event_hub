import type { LocalizedArray } from '~/types/i18n/localizedPage';

export type IndexFooterRaw = {
  email: {
    link: string,
    text: string,
  },
  social: Array<{
    icon: string,
    text: string,
    link: string,
  }>,
  text: LocalizedArray,
};
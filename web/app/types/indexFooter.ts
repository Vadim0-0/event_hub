import type { LocalizedArray } from '~/types/localizedPage';

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
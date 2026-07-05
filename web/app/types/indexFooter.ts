import type { I18nLocaleCode } from '../../i18n.options';

export type LocalizedScalar = Partial<Record<I18nLocaleCode, string>>;

export type LocalizedArray = Partial<Record<I18nLocaleCode, string[]>>;

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
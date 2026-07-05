import type { I18nLocaleCode } from '../../i18n.options';

export type LocalizedScalar = Partial<Record<I18nLocaleCode, string>>;

export type LocalizedArray = Partial<Record<I18nLocaleCode, string[]>>;

export type IndexPageRaw = {
  title: LocalizedScalar
  sections: {
    hero: {
      title: LocalizedArray
      text: LocalizedArray
      button: { to: string; text: LocalizedScalar }
    }
    howWork: {
      items: Array<{
        icon: string
        title: LocalizedArray
        text: LocalizedArray
      }>
    }
    forWork: {
      items: Array<{
        icon: string
        title: LocalizedArray
        text: LocalizedArray
      }>
      bards: number[]
    }
    advantages: {
      items: Array<
        | { icon: string; title: LocalizedArray; text: LocalizedArray }
        | { image: string }
      >
    }
  }
};
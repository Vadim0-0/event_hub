import type { I18nLocaleCode } from '~~/i18n.options';

export type LocalizedScalar = Partial<Record<I18nLocaleCode, string>>;
export type LocalizedArray = Partial<Record<I18nLocaleCode, string[]>>;

export interface BasePageData {
  title: LocalizedScalar;
  sections: Record<string, unknown>;
}
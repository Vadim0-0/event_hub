import type { I18nLocaleCode } from '~~/i18n.options';
import { locales, resolveI18nLocaleCode } from '~~/i18n.options';

export type LocaleSelectOption = {
  value: I18nLocaleCode
  label: { normal: string; collapsed: string }
};

export const languageOptions: LocaleSelectOption[] = locales.map((l) => ({
  value: l.code,
  label: {
    normal: l.name,
    collapsed: l.shortName,
  },
}));

export function useLocaleSwitch() {
  const { locale, setLocale } = useI18n();

  const selectedLocale = computed({
    get: () => resolveI18nLocaleCode(locale.value),
    set: (code: string) => {
      const next = resolveI18nLocaleCode(code)
      if (next === resolveI18nLocaleCode(locale.value)) return
      void setLocale(next)
    },
  });

  return {
    languageOptions,
    selectedLocale,
    locale,
  };
};
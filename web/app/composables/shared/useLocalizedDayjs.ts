import type { ConfigType } from 'dayjs';

import { resolveI18nLocaleCode } from '~~/i18n.options';

export function useLocalizedDayjs() {
  const dayjs = useDayjs();
  const { locale } = useI18n();

  return (input?: ConfigType) => {
    const code = resolveI18nLocaleCode(locale.value);
    return input === undefined ? dayjs().locale(code) : dayjs(input).locale(code);
  };
}

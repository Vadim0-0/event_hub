import en from 'dayjs/locale/en';
import ru from 'dayjs/locale/ru';

import { resolveI18nLocaleCode } from '~~/i18n.options';

const localeData = {
  en,
  ru,
} as const;

function applyDayjsLocale(dayjs: ReturnType<typeof useDayjs>, locale: string) {
  const code = resolveI18nLocaleCode(locale);
  dayjs.locale(code, localeData[code]);
}

export default defineNuxtPlugin({
  name: 'dayjs-i18n',
  dependsOn: ['i18n:plugin'],
  setup(nuxtApp) {
    const dayjs = useDayjs();
    const { locale } = useI18n();

    applyDayjsLocale(dayjs, locale.value);

    nuxtApp.hook('app:created', () => {
      applyDayjsLocale(dayjs, locale.value);
    });

    nuxtApp.hook('i18n:localeSwitched', ({ newLocale }) => {
      applyDayjsLocale(dayjs, newLocale);
    });
  },
});

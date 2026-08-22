import { pickScalar, pickArray, expandItems } from '~/composables/i18n/useLocalization';
import type { IndexFooterRaw } from '~/types/i18n/components/indexFooter';

export function mapIndexFooter(data: IndexFooterRaw, locale: string) {
  const currentYear = new Date().getFullYear()

  return {
    email: data.email,
    social: data.social,
    text: pickArray(data.text, locale).map(line => 
      line.replace('{{ currentYear }}', String(currentYear))
    ),
  };
}

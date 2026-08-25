import { pickScalar } from '~/composables/i18n/useLocalization';
import type { LocalizedScalar } from '~/types/i18n/localizedPage';
import type { MapRaw} from '~/types/i18n/components/map';

function mapNotification(
  notification: { 
    title: LocalizedScalar; 
    message: LocalizedScalar ;
  },
  locale: string,
) {
  return {
    title: pickScalar(notification.title, locale),
    message: pickScalar(notification.message, locale),
  }
};


export function mapMap(data: MapRaw, locale: string) {
  return {
    searchInput: {
      label: pickScalar(data.searchInput.label, locale),
      placeholder: pickScalar(data.searchInput.placeholder, locale),
    },

    loading: pickScalar(data.loading, locale),

    cancelButton: pickScalar(data.cancelButton, locale),
    confirmButton: pickScalar(data.confirmButton, locale),

    formErrors: {
      loadError: pickScalar(data.formErrors.loadError, locale),
    }
  }
};
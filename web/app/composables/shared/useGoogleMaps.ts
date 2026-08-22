/// <reference types="google.maps" />

import { setOptions, importLibrary } from '@googlemaps/js-api-loader';

let loaderPromise: Promise<typeof google> | null = null;

export function useGoogleMaps() {
  const config = useRuntimeConfig();

  function loadGoogleMaps() {
    if (!import.meta.client) {
      return Promise.reject(new Error('Google Maps is client-only'));
    }

    const apiKey = config.public.googleMapsApiKey as string;
    if (!apiKey) {
      return Promise.reject(new Error('NUXT_PUBLIC_GOOGLE_MAPS_API_KEY is missing'));
    }

    if (!loaderPromise) {
      setOptions({
        key: apiKey,
        v: 'weekly',
      });

      loaderPromise = Promise.all([
        importLibrary('maps'),
        importLibrary('marker'),
        importLibrary('geocoding'),
        importLibrary('places'),
      ]).then(() => google);
    }

    return loaderPromise;
  }

  return { loadGoogleMaps };
}

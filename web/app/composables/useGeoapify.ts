type GeoapifyFeature = {
  properties: {
    formatted?: string
    lat: number
    lon: number
  }
};

type GeoapifyResponse = {
  features: GeoapifyFeature[]
};

export function useGeoapify() {
  const config = useRuntimeConfig();
  const apiKey = computed(() => config.public.geoapifyApiKey as string);

  function assertApiKey() {
    if (!apiKey.value) {
      throw new Error('NUXT_PUBLIC_GEOAPIFY_API_KEY is missing');
    }
  }

  async function reverseGeocode(lat: number, lon: number): Promise<string> {
    assertApiKey();

    const url = new URL('https://api.geoapify.com/v1/geocode/reverse');
    url.searchParams.set('lat', String(lat));
    url.searchParams.set('lon', String(lon));
    url.searchParams.set('apiKey', apiKey.value);

    const data = await $fetch<GeoapifyResponse>(url.toString());
    const formatted = data.features[0]?.properties?.formatted;

    return formatted ?? `${lat.toFixed(6)}, ${lon.toFixed(6)}`;
  }

  async function autocomplete(text: string): Promise<GeoapifyFeature[]> {
    assertApiKey();
    if (!text.trim()) return [];

    const url = new URL('https://api.geoapify.com/v1/geocode/autocomplete');
    url.searchParams.set('text', text.trim());
    url.searchParams.set('apiKey', apiKey.value);
    url.searchParams.set('limit', '5');

    const data = await $fetch<GeoapifyResponse>(url.toString());
    return data.features ?? [];
  }

  function tileUrl(style = 'osm-bright') {
    assertApiKey();
    return `https://maps.geoapify.com/v1/tile/${style}/{z}/{x}/{y}.png?apiKey=${apiKey.value}`;
  }

  return {
    apiKey,
    reverseGeocode,
    autocomplete,
    tileUrl,
  };
}
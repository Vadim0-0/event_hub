<script setup lang="ts">
  import type * as Leaflet from 'leaflet';
  import type { LatLngTuple, LeafletMouseEvent, Map as LeafletMap, Marker } from 'leaflet';
  import '@geoapify/geocoder-autocomplete/styles/minimal.css';

  export type MapLocation = {
    location: string
    latitude: number
    longitude: number
  };

  const props = withDefaults(defineProps<{
    latitude?: number | null
    longitude?: number | null
    zoom?: number
    readonly?: boolean
  }>(), {
    latitude: null,
    longitude: null,
    zoom: 12,
    readonly: false,
  });

  const emit = defineEmits<{
    select: [MapLocation]
  }>();

  const { reverseGeocode, tileUrl } = useGeoapify();

  const mapContainer = ref<HTMLElement | null>(null);
  const searchContainer = ref<HTMLElement | null>(null);
  const isLoading = ref(true);
  const loadError = ref('');

  type GeoapifyAutocomplete = {
    setValue: (value: string) => void
    on: (
      event: 'select',
      callback: (value: { properties: { lat: number; lon: number; formatted?: string } }) => void,
    ) => void
  };

  let map: LeafletMap | null = null;
  let marker: Marker | null = null;
  let L: typeof Leaflet | null = null;
  let autocomplete: GeoapifyAutocomplete | null = null;

  const defaultCenter: LatLngTuple = [55.7558, 37.6173];

  function getCenter(): LatLngTuple {
    if (props.latitude != null && props.longitude != null) {
      return [props.latitude, props.longitude];
    }
    return defaultCenter;
  }

  async function emitLocation(lat: number, lng: number) {
    const location = await reverseGeocode(lat, lng);
    autocomplete?.setValue(location);
    emit('select', { location, latitude: lat, longitude: lng });
  }

  function setMarker(lat: number, lng: number) {
    if (!map || !L) return;

    if (!marker) {
      const nextMarker = L.marker([lat, lng], { draggable: !props.readonly }).addTo(map);
      marker = nextMarker;

      if (!props.readonly) {
        nextMarker.on('dragend', async () => {
          const pos = nextMarker.getLatLng();
          await emitLocation(pos.lat, pos.lng);
        });
      }
    } else {
      marker.setLatLng([lat, lng]);
    }

    map.panTo([lat, lng]);
  }

  async function initMap() {
    if (!import.meta.client || !mapContainer.value) return;

    try {
      const leafletModule = await import('leaflet');
      L = 'default' in leafletModule
        ? (leafletModule as { default: typeof Leaflet }).default
        : (leafletModule as typeof Leaflet);
      await import('leaflet/dist/leaflet.css');

      const leafletMap = L.map(mapContainer.value, {
        center: getCenter(),
        zoom: props.zoom,
      });
      map = leafletMap;

      L.tileLayer(tileUrl('osm-bright'), {
        maxZoom: 20,
        attribution: 'Powered by <a href="https://www.geoapify.com/" target="_blank">Geoapify</a>',
      }).addTo(leafletMap);

      if (props.latitude != null && props.longitude != null) {
        setMarker(props.latitude, props.longitude);
      }

      if (!props.readonly) {
        leafletMap.on('click', async (event: LeafletMouseEvent) => {
          const { lat, lng } = event.latlng;
          setMarker(lat, lng);
          await emitLocation(lat, lng);
        });
      }

      if (!props.readonly && searchContainer.value) {
        const { GeocoderAutocomplete } = await import('@geoapify/geocoder-autocomplete');

        autocomplete = new GeocoderAutocomplete(
          searchContainer.value,
          useRuntimeConfig().public.geoapifyApiKey as string,
          { placeholder: 'Search address...' },
        );

        autocomplete.on('select', (value: { properties: { lat: number; lon: number; formatted?: string } }) => {
          const { lat, lon, formatted } = value.properties;
          setMarker(lat, lon);
          emit('select', {
            location: formatted ?? `${lat}, ${lon}`,
            latitude: lat,
            longitude: lon,
          });
        });
      }
    } catch (e) {
      loadError.value = e instanceof Error ? e.message : 'Failed to load map';
    } finally {
      isLoading.value = false;
    }
  }

  watch(
    () => [props.latitude, props.longitude] as const,
    ([lat, lng]) => {
      if (lat == null || lng == null || !map) return;
      setMarker(lat, lng);
    },
  );

  onMounted(() => {
    void initMap();
  });

  onUnmounted(() => {
    map?.remove();
    map = null;
    marker = null;
    autocomplete = null;
    L = null;
  });
</script>

<template>
  <div class="fixed top-0 left-0 w-full h-full z-100 p-10 bg-overlay">
    <div 
      class="
        flex flex-col w-full h-full overflow-hidden p-4
        bg-main rounded-sm
      "
    >
      <button 
        type="button"
        class="group ml-auto mr-2 mb-1"
      >
        <Icon name="akar-icons:cross" 
          class="
            size-6 text-text-main
            transition-transform transition-300 ease-in-out
            group-hover:rotate-90
          " 
        />
      </button>
      <label class="ui-input shrink-0 mb-4">
        <span class="ui-input__label">Search address</span>
        <div ref="searchContainer" class="ui-input__field" />
      </label>

      <div class="relative flex flex-1 z-1 rounded-sm overflow-hidden mb-4">
        <div
          v-if="isLoading"
          class="absolute inset-0 z-10 flex items-center justify-center bg-primary-light text-body-sm text-text-secondary"
        >
          Loading map...
        </div>

        <p
          v-else-if="loadError"
          class="absolute inset-0 z-10 flex items-center justify-center p-4 text-center text-error text-body-sm"
        >
          {{ loadError }}
        </p>

        <div ref="mapContainer" class="w-full h-full" />
      </div>

      <div class="flex justify-end gap-2">
        <UiButton style-type="cancel">
          Cancel
        </UiButton>
        <UiButton>
          Confirm
        </UiButton>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
  .ui-input__field {
    :deep(.geoapify-autocomplete-input) {
      padding: 20px 10px;
      color: var(--color-text-main);
      background-color: var(--color-third);
    }
  }

  :deep(.geoapify-autocomplete-items) {
    background-color: var(--color-main);
    border: 1px solid var(--color-fifth);
    border-radius: 5px;
    box-shadow: 0 6px 15px -1px rgba(33, 33, 33, 0.1);
  }

  :deep(.geoapify-autocomplete-item) {
    color: var(--color-text-main);
    background-color: var(--color-main);

    .main-part {
      color: var(--color-text-main);
    }

    .secondary-part {
      color: var(--color-text-secondary);
    }
  }

  :deep(.geoapify-autocomplete-items .active),
  :deep(.geoapify-autocomplete-item:hover) {
    background-color: var(--color-primary-light);
  }
</style>

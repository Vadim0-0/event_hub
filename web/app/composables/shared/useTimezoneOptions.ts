type TimezoneOption = {
  value: string
  label: string
};

function formatTimezoneLabel(timezone: string, locale: string) {
  try {
    const parts = new Intl.DateTimeFormat(locale, {
      timeZone: timezone,
      timeZoneName: 'shortOffset',
    }).formatToParts(new Date());

    const offset = parts.find((part) => part.type === 'timeZoneName')?.value ?? '';
    const city = timezone.split('/').pop()?.replace(/_/g, ' ') ?? timezone;

    return offset ? `${city} (${offset})` : city;
  } catch {
    return timezone;
  }
}

function detectTimezone() {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';
  } catch {
    return 'UTC';
  }
}

export function useTimezoneOptions() {
  const { locale } = useI18n();

  const detectedTimezone = detectTimezone();

  const timezoneOptions = computed<TimezoneOption[]>(() => {
    if (import.meta.server) {
      return [{ value: 'UTC', label: 'UTC' }];
    }

    const all = Intl.supportedValuesOf('timeZone');

    const sorted = [...all].sort((a, b) =>
      formatTimezoneLabel(a, locale.value).localeCompare(
        formatTimezoneLabel(b, locale.value),
      ),
    );

    const withoutDetected = sorted.filter((tz) => tz !== detectedTimezone);

    const options = withoutDetected.map((tz) => ({
      value: tz,
      label: formatTimezoneLabel(tz, locale.value),
    }));

    if (detectedTimezone !== 'UTC' && all.includes(detectedTimezone)) {
      options.unshift({
        value: detectedTimezone,
        label: `${formatTimezoneLabel(detectedTimezone, locale.value)}`,
      });
    }

    return options;
  });

  return {
    detectedTimezone,
    timezoneOptions,
  };
}
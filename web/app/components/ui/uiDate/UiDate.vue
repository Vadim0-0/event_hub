<script setup lang="ts">

  // === 1. CONFIG ===
  defineOptions({ inheritAttrs: false });

  const dayjs = useDayjs()

  interface Props {
    label?: string
    placeholder?: string
    id?: string
    class?: string
    disabled?: boolean
    errorMessage?: string
    min?: string              // 'YYYY-MM-DD'
    disablePast?: boolean
  };

  const props = withDefaults(defineProps<Props>(), {
    label: '',
    placeholder: 'Select date',
    id: undefined,
    class: '',
    disabled: false,
    errorMessage: '',
    min: undefined,
    disablePast: true,
  });

  const modelValue = defineModel<string>({ default: '' }); // API: YYYY-MM-DD
  const inputText = ref('');                               // UI:  DD.MM.YYYY

  const isOpen = ref(false);
  const fieldRef = ref<HTMLElement | null>(null);
  const viewDate = ref(dayjs());


  // === 2. MIN DATE ===
  const minDate = computed(() => {
    if (props.min) return props.min;
    if (props.disablePast) return dayjs().format('YYYY-MM-DD');
    return undefined;
  });


  // === 3. PARSE ===
  function parseDateOnly(value: string) {
    const trimmed = value.trim();
    if (!/^\d{2}\.\d{2}\.\d{4}$/.test(trimmed)) return null;

    const [day, month, year] = trimmed.split('.').map(Number) as [number, number, number];
    const parsed = dayjs(new Date(year, month - 1, day));

    if (!parsed.isValid()) return null;

    if (
      parsed.date() !== day ||
      parsed.month() !== month - 1 ||
      parsed.year() !== year
    ) {
      return null
    };

    return parsed;
  };

  function isBeforeMin(date: ReturnType<typeof dayjs>) {
    if (!minDate.value) return false;
    return date.isBefore(dayjs(minDate.value), 'day');
  };

  function parseDateInput(value: string) {
    const parsed = parseDateOnly(value);
    if (!parsed || isBeforeMin(parsed)) return null;
    return parsed;
  };


  // === 4. INPUT ===
  function formatDateMask(raw: string): string {
    const digits = raw.replace(/\D/g, '').slice(0, 8);

    if (digits.length <= 2) return digits;
    if (digits.length <= 4) return `${digits.slice(0, 2)}.${digits.slice(2)}`;
    return `${digits.slice(0, 2)}.${digits.slice(2, 4)}.${digits.slice(4)}`;
  };

  function onKeydown(event: KeyboardEvent) {
    const allowed = [
      'Backspace', 'Delete', 'ArrowLeft', 'ArrowRight',
      'Tab', 'Home', 'End',
    ];

    if (allowed.includes(event.key)) return;
    if (event.ctrlKey || event.metaKey) return;
    if (!/^\d$/.test(event.key)) event.preventDefault();
  };

  function onInput(event: Event) {
    const input = event.target as HTMLInputElement;
    inputText.value = formatDateMask(input.value);

    if (inputText.value.length === 10) {
      const parsed = parseDateInput(inputText.value);
      modelValue.value = parsed ? parsed.format('YYYY-MM-DD') : '';
      return;
    };

    modelValue.value = '';
  };

  function onInputBlur() {
    if (!inputText.value.trim()) {
      modelValue.value = '';
      return;
    };

    const parsed = parseDateOnly(inputText.value);

    if (!parsed || isBeforeMin(parsed)) {
      inputText.value = modelValue.value
        ? dayjs(modelValue.value).format('DD.MM.YYYY')
        : ''
      return;
    };

    modelValue.value = parsed.format('YYYY-MM-DD');
    inputText.value = parsed.format('DD.MM.YYYY');
  }


  // === 5. INPUT STATE ===
  const inputState = computed<'empty' | 'typing' | 'valid' | 'invalid' | 'past'>(() => {
    const value = inputText.value;

    if (!value) return 'empty';
    if (value.length < 10) return 'typing';

    const parsed = parseDateOnly(value);
    if (!parsed) return 'invalid';
    if (isBeforeMin(parsed)) return 'past';

    return 'valid';
  });

  const hasInputError = computed(() =>
    inputState.value === 'invalid'
    || inputState.value === 'past'
    || Boolean(props.errorMessage?.trim()),
  );


  // === 6. CALENDAR UI ===
  function openCalendar() {
    if (props.disabled) return;

    isOpen.value = true;

    if (modelValue.value) {
      viewDate.value = dayjs(modelValue.value)
      return;
    };

    const parsed = parseDateOnly(inputText.value);
    if (parsed) viewDate.value = parsed;
  };

  function closeCalendar() {
    isOpen.value = false;
  };

  onClickOutside(fieldRef, closeCalendar);

  const {
    onBeforeEnter: onSelectorBeforeEnter,
    onEnter: onSelectorEnter,
    onAfterEnter: onSelectorAfterEnter,
    onBeforeLeave: onSelectorBeforeLeave,
    onLeave: onSelectorLeave,
  } = useHeightTransition({ duration: 300, marginTop: 5 });

  const monthLabel = computed(() => viewDate.value.format('MMMM YYYY'));

  function prevMonth() {
    viewDate.value = viewDate.value.subtract(1, 'month');
  };

  function nextMonth() {
    viewDate.value = viewDate.value.add(1, 'month');
  };


  // === 7. CALENDAR LOGIC ===
  const weekDays = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];

  const calendarDays = computed(() => {
    const start = viewDate.value.startOf('month').startOf('week').add(1, 'day');
    const end = viewDate.value.endOf('month').endOf('week').add(1, 'day');

    const days = [];
    let current = start;

    while (current.isBefore(end)) {
      days.push(current);
      current = current.add(1, 'day');
    };

    return days;
  });

  function isDisabledDay(day: ReturnType<typeof dayjs>) {
    if (!minDate.value) return false;
    return day.isBefore(dayjs(minDate.value), 'day');
  };

  function selectDate(day: ReturnType<typeof dayjs>) {
    if (isDisabledDay(day)) return;

    modelValue.value = day.format('YYYY-MM-DD');
    inputText.value = day.format('DD.MM.YYYY');
    closeCalendar();
  };

  function setToday() {
    const today = dayjs();

    if (isDisabledDay(today)) return;

    modelValue.value = today.format('YYYY-MM-DD');
    inputText.value = today.format('DD.MM.YYYY');
    viewDate.value = today;
    closeCalendar();
  };

  function clearDate() {
    modelValue.value = '';
    inputText.value = '';
    closeCalendar();
  };


  // === 8. SYNC ===
  watch(
    modelValue,
    (value) => {
      const formatted = value
        ? dayjs(value).format('DD.MM.YYYY')
        : ''

      if (formatted !== inputText.value) {
        inputText.value = formatted
      }
    },
    { immediate: true },
  );

</script>

<template>
  <label for="" class="ui-date" :class="[{ error: hasInputError }, props.class]">
    <span class="ui-date__label">
      Название
    </span>

    <div ref="fieldRef" class="ui-date__body">
      <div class="ui-date__body-field">
        <button
          type="button"
          class="ui-date__body-field__open"
          :disabled="props.disabled"
          @click.stop="openCalendar"
        >
          <Icon name="fe:calendar" mode="svg" />
        </button>
        <input
          :id="props.id"
          type="text"
          inputmode="numeric"
          maxlength="10"
          :placeholder="props.placeholder || 'DD.MM.YYYY'"
          :disabled="props.disabled"
          :value="inputText"
          :class="{ 'is-invalid': inputState === 'invalid' }"
          @input="onInput"
          @keydown="onKeydown"
          @blur="onInputBlur"
          @keydown.enter="onInputBlur"
        >
      </div>
  
      <Transition
        :css="false"
        @before-enter="onSelectorBeforeEnter"
        @enter="onSelectorEnter"
        @after-enter="onSelectorAfterEnter"
        @before-leave="onSelectorBeforeLeave"
        @leave="onSelectorLeave"
      >
        <div v-if="isOpen" class="ui-date__body-wrap">
          <div class="date-selector">
            <div class="date-selector__top">
              <button type="button" class="date-selector__top-btn prev-btn" @click="prevMonth">
                <Icon name="eva:arrow-up-fill" mode="svg" />
              </button>
              <div class="date-selector__top-name">
                <p>{{ monthLabel }}</p>
              </div>
              <button type="button" class="date-selector__top-btn next-btn" @click="nextMonth">
                <Icon name="eva:arrow-up-fill" mode="svg" />
              </button>
            </div>  
            <div class="date-selector__calendar">
  
              <div class="date-selector__calendar-weekdays">
                <span v-for="day in weekDays" :key="day">{{ day }}</span>
              </div>
  
              <div class="date-selector__calendar-grid">
                <button
                  v-for="day in calendarDays"
                  :key="day.format('YYYY-MM-DD')"
                  type="button"
                  class="date-selector__day"
                  :class="{
                    'is-other-month': !day.isSame(viewDate, 'month'),
                    'is-selected': modelValue === day.format('YYYY-MM-DD'),
                    'is-today': day.isSame(dayjs(), 'day'),
                    'is-disabled': isDisabledDay(day),
                  }"
                  :disabled="isDisabledDay(day)"
                  @click="selectDate(day)"
                >
                  {{ day.date() }}
                </button>
              </div>
    
            </div>
            <div class="date-selector__bottom">
              <button type="button" @click="clearDate">
                Clear
              </button>
              <button type="button" @click="setToday">
                Today
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </div>


    <div class="ui-date__error" v-if="inputState === 'invalid'">
      <p>
        Invalid date format
      </p>
    </div>
    <div v-if="props.errorMessage" class="ui-date__error">
      <p>{{ props.errorMessage }}</p>
    </div>
  </label>
</template>

<style lang="scss">

  .ui-date {
    display: flex;
    flex-direction: column;
    width: 100%;
    outline: none;
    border: none;

    &__label {
      margin-bottom: 5px;
      color: var(--color-text-main);
      font-size: var(--text-body-sm);
      font-weight: 500;
    }

    &__body {

      &-field {
        position: relative;
        z-index: 2;
        width: 100%;
  
        &__open {
          position: absolute;
          top: 50%;
          right: 5px;
          transform: translateY(-50%);
  
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
  
          transition: opacity 0.3s ease-in-out;
  
          & svg {
            width: 20px;
            height: 20px;
            color: var(--color-primary-light-2);
            transition: color 0.3s ease-in-out;
          }
  
          &:hover {
            
            & svg {
              color: var(--color-primary);
            }
          }
        }
  
        & input {
          padding: 16px 12px;
          width: 100%;
          outline: none;
          border: none;
          box-shadow: none;
          background-color: var(--color-third);
          border-radius: 5px;
          transition: all 0.3s ease-in-out;
    
          color: var(--color-text-main);
          font-size: var(--text-body-xl);
    
          &::-webkit-outer-spin-button,
          &::-webkit-inner-spin-button {
            -moz-appearance: textfield;
            appearance: textfield;
            -webkit-appearance: none;
            margin: 0;
          }
    
          &:focus {
            outline: none;
            border-color: var(--color-primary-hover);
          }
    
          &:disabled {
            opacity: 0.6;
            cursor: not-allowed;
          }
        }
  
        &:hover {
          & .ui-input__field-control {
            opacity: 1;
          }
        }
      }

      &-wrap {
        position: relative;
        z-index: 1;
        margin-top: 5px;
        overflow: hidden;

        & .date-selector {
          z-index: 5;
  
          display: flex;
          flex-direction: column;
          gap: 20px;
          width: 100%;
  
          padding: 10px;
  
          background-color: var(--color-third);
          border-radius: 5px;
  
          &__top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 5px;
  
            &-btn {
  
              & svg {
                color: var(--color-text-main);
              }
  
              &.prev-btn {
                transform: rotate(-90deg);
              }
  
              &.next-btn {
                transform: rotate(90deg);
              }
            }
  
            &-name {
              font-size: 16px;
              font-weight: 500;
              color: var(--color-text-main);
            }
          }
  
          &__calendar {
            display: flex;
            flex-direction: column;
            gap: 20px;
  
            &-weekdays {
              display: grid;
              grid-template-columns: repeat(7, 1fr);
  
              & span {
                text-align: center;
                font-size: 16px;
                color: var(--color-text-main);
              }
            }
  
            &-grid {
              display: grid;
              grid-template-columns: repeat(7, 1fr);
              gap: 2px 5px;
  
              & button {
                padding: 2px;
  
                border-radius: 5px;
                text-align: center;
                font-size: 16px;
                color: var(--color-text-main);
  
                &:hover {
                  background-color: var(--color-primary-light-2);
                }
  
                &.is-selected {
                  background-color: var(--color-primary);
  
                  color: var(--color-main);
                }
              }
            }
          }
  
          &__bottom {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            padding: 0 10px;
  
            & button {
              font-size: 16px;
              font-weight: 500;
              color: var(--color-text-main);
            }
          }
        }
      }
    }

    &__error {
      margin-top: 10px;
      font-weight: 500;
      font-size: var(--text-body-xl);
      color: var(--color-error);
    }

    &.error {

      & input {
        color: var(--color-error) !important;
        border-color: var(--color-error) !important;
      }
    }
  }

</style>

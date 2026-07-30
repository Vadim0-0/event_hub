<script setup lang="ts">

  // === 1. CONFIG ===
  defineOptions({ inheritAttrs: false });

  interface Props {
    label?: string
    placeholder?: string
    id?: string
    class?: string
    disabled?: boolean
    errorMessage?: string
  }

  const props = withDefaults(defineProps<Props>(), {
    label: '',
    placeholder: 'Select time',
    id: undefined,
    class: '',
    disabled: false,
    errorMessage: '',
  });

  const modelValue = defineModel<string>({ default: '' }); // API: "HH:mm" 24h


  // === 2. TYPES ===
  type DialMode = 'hours' | 'minutes';
  type Period = 'AM' | 'PM';


  // === 3. POPUP STATE ===
  const isOpen = ref(false);
  const fieldRef = ref<HTMLElement | null>(null);
  const dialsRef = ref<HTMLElement | null>(null);
  const inputText = ref('');
  const period = ref<Period>('AM');

  // Snapshot taken on open — used by CANCEL
  const snapshotHour = ref(12);
  const snapshotMinute = ref(0);
  const snapshotPeriod = ref<Period>('AM');


  // === 4. CLOCK STATE ===
  const dialMode = ref<DialMode>('hours');
  const selectedHour = ref(12);
  const selectedMinute = ref(0);
  const previewHour = ref(12);
  const previewMinute = ref(0);
  const hourText = ref('12');
  const minuteText = ref('00');
  const handHour = ref(12);
  const handMinute = ref(0);
  const handVisible = ref(false);
  const dialLocked = ref(false);

  const hours = [12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
  const allMinutes = Array.from({ length: 60 }, (_, i) => i);

  const amId = computed(() => `${props.id ?? 'time'}-am`);
  const pmId = computed(() => `${props.id ?? 'time'}-pm`);
  const radiosName = computed(() => `${props.id ?? 'time'}-period`);

  const hasInputError = computed(() => Boolean(props.errorMessage?.trim()));


  // === 5. HELPERS ===
  function hourAngle(hour: number) {
    const index = hour === 12 ? 0 : hour;
    return index * 30;
  }

  function minuteAngle(minute: number) {
    return (minute % 60) * 6;
  }

  function formatMinute(minute: number) {
    return String(minute).padStart(2, '0');
  }

  function formatTime(hour: number, minute: number, sign: Period) {
    return `${hour}:${formatMinute(minute)} ${sign}`;
  }

  function syncTextsFromPreview() {
    hourText.value = String(previewHour.value);
    minuteText.value = formatMinute(previewMinute.value);
  }

  function parseModel(value: string): { hour: number; minute: number; period: Period } | null {
    if (!/^\d{2}:\d{2}$/.test(value)) return null;

    const [h24, minute] = value.split(':').map(Number) as [number, number];
    if (h24 < 0 || h24 > 23 || minute < 0 || minute > 59) return null;

    const periodValue: Period = h24 >= 12 ? 'PM' : 'AM';
    const hour = h24 % 12 === 0 ? 12 : h24 % 12;

    return { hour, minute, period: periodValue };
  }

  function toModel(hour: number, minute: number, sign: Period): string {
    let h24 = hour % 12;
    if (sign === 'PM') h24 += 12;
    if (sign === 'AM' && hour === 12) h24 = 0;
    if (sign === 'PM' && hour === 12) h24 = 12;

    return `${String(h24).padStart(2, '0')}:${formatMinute(minute)}`;
  }

  function applyParsedTime(parsed: { hour: number; minute: number; period: Period }) {
    selectedHour.value = parsed.hour;
    selectedMinute.value = parsed.minute;
    period.value = parsed.period;
    previewHour.value = parsed.hour;
    previewMinute.value = parsed.minute;
    handHour.value = parsed.hour;
    handMinute.value = parsed.minute;
    syncTextsFromPreview();
  }


  // === 6. SYNC MODEL → UI ===
  watch(
    modelValue,
    (value) => {
      const parsed = parseModel(value);

      if (!parsed) {
        inputText.value = '';
        return;
      }

      applyParsedTime(parsed);
      inputText.value = formatTime(parsed.hour, parsed.minute, parsed.period);
    },
    { immediate: true },
  );


  // === 7. POPUP OPEN / CLOSE ===
  function openSelector() {
    if (props.disabled) return;

    snapshotHour.value = selectedHour.value;
    snapshotMinute.value = selectedMinute.value;
    snapshotPeriod.value = period.value;

    previewHour.value = selectedHour.value;
    previewMinute.value = selectedMinute.value;
    handHour.value = selectedHour.value;
    handMinute.value = selectedMinute.value;
    syncTextsFromPreview();

    dialMode.value = 'hours';
    dialLocked.value = false;
    handVisible.value = false;
    isOpen.value = true;
  }

  function closeSelector() {
    isOpen.value = false;
    dialLocked.value = false;
    handVisible.value = false;
  }

  // Smooth open/close without grid 0fr→1fr end-snap
  const {
    onBeforeEnter: onSelectorBeforeEnter,
    onEnter: onSelectorEnter,
    onAfterEnter: onSelectorAfterEnter,
    onBeforeLeave: onSelectorBeforeLeave,
    onLeave: onSelectorLeave,
  } = useHeightTransition({ duration: 300, marginTop: 10 });

  function cancelSelector() {
    selectedHour.value = snapshotHour.value;
    selectedMinute.value = snapshotMinute.value;
    period.value = snapshotPeriod.value;
    previewHour.value = snapshotHour.value;
    previewMinute.value = snapshotMinute.value;
    handHour.value = snapshotHour.value;
    handMinute.value = snapshotMinute.value;
    syncTextsFromPreview();
    closeSelector();
  }

  function confirmSelector() {
    selectedHour.value = previewHour.value;
    selectedMinute.value = previewMinute.value;

    modelValue.value = toModel(
      selectedHour.value,
      selectedMinute.value,
      period.value,
    );

    inputText.value = formatTime(
      selectedHour.value,
      selectedMinute.value,
      period.value,
    );

    closeSelector();
  }

  onClickOutside(fieldRef, () => {
    if (!isOpen.value) return;
    cancelSelector();
  });


  // === 8. DIAL HOVER / SELECT ===
  function onHourEnter(hour: number) {
    if (dialLocked.value) return;
    previewHour.value = hour;
    handHour.value = hour;
    hourText.value = String(hour);
    handVisible.value = true;
  }

  function onMinuteEnter(minute: number) {
    previewMinute.value = minute;
    handMinute.value = minute;
    minuteText.value = formatMinute(minute);
    handVisible.value = true;
  }

  // Restore only when pointer leaves the whole dial
  function restoreHourPreview() {
    if (dialLocked.value) return;
    previewHour.value = selectedHour.value;
    hourText.value = String(selectedHour.value);
    handVisible.value = false;
  }

  function restoreMinutePreview() {
    previewMinute.value = selectedMinute.value;
    minuteText.value = formatMinute(selectedMinute.value);
    handVisible.value = false;
  }

  function selectHour(hour: number) {
    if (dialLocked.value) return;
    selectedHour.value = hour;
    previewHour.value = hour;
    hourText.value = String(hour);
    handHour.value = hour;
    dialMode.value = 'minutes';
    handVisible.value = true;
  }

  function selectMinute(minute: number) {
    selectedMinute.value = minute;
    previewMinute.value = minute;
    minuteText.value = formatMinute(minute);
    dialLocked.value = true;
    dialMode.value = 'hours';
    handHour.value = selectedHour.value;
    handVisible.value = false;
  }

  function onDialsMouseLeave() {
    requestAnimationFrame(() => {
      if (dialsRef.value?.matches(':hover')) return;

      if (dialMode.value === 'hours') {
        restoreHourPreview();
      } else {
        restoreMinutePreview();
      }

      dialLocked.value = false;
    });
  }


  // === 9. KEYBOARD INPUT ===
  function onTimeKeydown(e: KeyboardEvent) {
    const allowed = ['Backspace', 'Delete', 'Tab', 'ArrowLeft', 'ArrowRight'];
    if (allowed.includes(e.key) || e.ctrlKey || e.metaKey) return;
    if (!/^\d$/.test(e.key)) e.preventDefault();
  }

  function onHourInput(e: Event) {
    const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '').slice(0, 2);
    hourText.value = raw;
    if (raw === '') return;

    const n = Number(raw);

    if (raw.length === 1) {
      if (n >= 1 && n <= 9) {
        previewHour.value = n;
        handHour.value = n;
      }
      return;
    }

    if (n >= 1 && n <= 12) {
      previewHour.value = n;
      selectedHour.value = n;
      handHour.value = n;
      hourText.value = String(n);
    } else {
      hourText.value = String(previewHour.value);
    }
  }

  function onMinuteInput(e: Event) {
    const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '').slice(0, 2);
    minuteText.value = raw;
    if (raw === '') return;

    const n = Number(raw);

    if (n >= 0 && n <= 59) {
      previewMinute.value = n;
      selectedMinute.value = n;
      handMinute.value = n;
    } else if (raw.length === 2) {
      minuteText.value = formatMinute(previewMinute.value);
    }
  }

  function onHourBlur() {
    let n = Number(hourText.value);
    if (!hourText.value || n < 1 || n > 12) n = selectedHour.value || 12;
    selectedHour.value = n;
    previewHour.value = n;
    hourText.value = String(n);
  }

  function onMinuteBlur(e: FocusEvent) {
    let n = Number(minuteText.value);
    if (!minuteText.value || n < 0 || n > 59) n = selectedMinute.value;
    selectedMinute.value = n;
    previewMinute.value = n;
    minuteText.value = formatMinute(n);

    const next = e.relatedTarget as Node | null;
    if (next && dialsRef.value?.contains(next)) return;

    dialMode.value = 'hours';
    handHour.value = selectedHour.value;
    handVisible.value = false;
  }

  function onHourFocus() {
    dialMode.value = 'hours';
    dialLocked.value = false;
  }

  function onMinuteFocus() {
    dialMode.value = 'minutes';
  }

</script>

<template>
  <label
    class="ui-time"
    :class="[{ error: hasInputError }, props.class]"
  >
    <span v-if="props.label" class="ui-time__label">
      {{ props.label }}
    </span>

    <div ref="fieldRef" class="ui-time__body">
      <div class="ui-time__body-field">
        <button
          type="button"
          class="ui-time__body-field__open"
          :disabled="props.disabled"
          @click.stop="openSelector"
        >
          <Icon name="ic:outline-watch-later" mode="svg" />
        </button>
        <input
          :id="props.id"
          type="text"
          :value="inputText"
          :placeholder="props.placeholder"
          :disabled="props.disabled"
          readonly
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
        <div v-if="isOpen" class="ui-time__body-wrap">
          <div class="time-selector">
            <div class="time-selector__top">
              <p>
                SELECT TIME
              </p>
            </div>
      
            <div class="time-selector__fields">
              <div class="time-selector__fields-inputs">
                <input
                  type="text"
                  inputmode="numeric"
                  maxlength="2"
                  :value="hourText"
                  @focus="onHourFocus"
                  @input="onHourInput"
                  @blur="onHourBlur"
                  @keydown="onTimeKeydown"
                >
                <span>:</span>
                <input
                  type="text"
                  inputmode="numeric"
                  maxlength="2"
                  :value="minuteText"
                  @focus="onMinuteFocus"
                  @input="onMinuteInput"
                  @blur="onMinuteBlur"
                  @keydown="onTimeKeydown"
                >
              </div>
              <div class="time-selector__fields-signs">
                <label :for="amId" class="time-selector__fields-signs__label">
                  <input type="radio" :id="amId" :name="radiosName" value="AM" v-model="period">
                  <span class="time-selector__fields-signs__label-custom">
                    AM
                  </span>
                </label>
                <label :for="pmId" class="time-selector__fields-signs__label">
                  <input type="radio" :id="pmId" :name="radiosName" value="PM" v-model="period">
                  <span class="time-selector__fields-signs__label-custom">
                    PM
                  </span>
                </label>
              </div>
            </div>
      
            <div
              ref="dialsRef"
              class="time-selector__dials"
              :class="{ 'is-locked': dialLocked }"
              @mousedown.prevent
              @mouseleave="onDialsMouseLeave"
            >
      
              <Transition name="clock-face-anim" mode="out-in">
                <div
                  v-if="dialMode === 'hours'"
                  key="hours"
                  class="clock-face"
                >
                  <div
                    class="clock-face__hand hour-hand"
                    :class="{ 'is-visible': handVisible }"
                    :style="{ '--angle': `${hourAngle(handHour)}deg` }"
                  />
      
                  <div class="clock-face__pivot" />
      
                  <button
                    v-for="hour in hours"
                    :key="hour"
                    type="button"
                    class="clock-face__number"
                    :style="{ '--angle': `${hourAngle(hour)}deg` }"
                    @mouseenter="onHourEnter(hour)"
                    @click="selectHour(hour)"
                  >
                  {{ hour }}
                  </button>
                </div>
      
                <div
                  v-else
                  key="minutes"
                  class="clock-face"
                >
                  <div
                    class="clock-face__hand minute-hand"
                    :class="{ 'is-visible': handVisible }"
                    :style="{ '--angle': `${minuteAngle(handMinute)}deg` }"
                  />
      
                  <div class="clock-face__pivot" />
      
                  <button
                    v-for="minute in allMinutes"
                    :key="minute"
                    type="button"
                    class="clock-face__number"
                    :class="{
                      'is-label': minute % 5 === 0,
                      'is-tick': minute % 5 !== 0,
                    }"
                    :style="{ '--angle': `${minuteAngle(minute)}deg` }"
                    @mouseenter="onMinuteEnter(minute)"
                    @click="selectMinute(minute)"
                  >
                    <span v-if="minute % 5 === 0">
                      {{ formatMinute(minute) }}
                    </span>
                  </button>
                </div>
              </Transition>
              
            </div>
      
            <div class="time-selector__bottom">
              <button type="button" @click="cancelSelector">
                CANCEL
              </button>
              <button type="button" @click="confirmSelector">
                OK
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </div>

    <div v-if="props.errorMessage" class="ui-time__error">
      <p>{{ props.errorMessage }}</p>
    </div>
  </label>
</template>

<style lang="scss">

  .ui-time {
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
      width: 100%;

      &-field {
        position: relative;
        width: 100%;
        z-index: 2;

        &__open {
          position: absolute;
          top: 50%;
          right: 8px;
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

        & > input {
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
        margin-top: 10px;
        overflow: hidden;

        & .time-selector {
          display: flex;
          flex-direction: column;
          gap: 20px;
          width: 100%;
    
          padding: 10px;
    
          background-color: var(--color-third);
          border-radius: 5px;
    
          &__top {
    
            font-size: 14px;
            font-weight: 400;
            color: var(--color-text-main);
          }
    
          &__fields {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
    
            &-inputs {
              display: flex;
              align-items: center;
              justify-content: center;
              gap: 5px;
    
              & input {
                padding: 0;
                width: 70px;
                height: 70px;
                background-color: var(--color-main);
    
                text-align: center;
                font-size: 32px;
                font-weight: 600;
                color: var(--color-text-main);
                
                outline: none;
                border: none;
                box-shadow: none;
                border-radius: 5px;
    
                &:nth-child(1) {
                  background-color: var(--color-primary-light-2);
                  color: var(--color-main);
                }
    
                &::-webkit-outer-spin-button,
                &::-webkit-inner-spin-button {
                  -moz-appearance: textfield;
                  appearance: textfield;
                  -webkit-appearance: none;
                  margin: 0;
                }
              }
    
              & span {
                font-size: 32px;
                font-weight: 800;
                color: var(--color-text-main);
              }
            }
    
            &-signs {
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: center;
    
              overflow: hidden;
              border-radius: 4px;
    
              border: 1px solid var(--color-fifth);
              background-color: var(--color-main);
    
              &__label {
                position: relative;
                overflow: hidden;
    
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
    
                cursor: pointer;
    
                & input {
                  position: absolute;
                  top: 0;
                  left: 0;
                  width: 100%;
                  height: 100%;
                  opacity: 0;
                  visibility: hidden;
    
                  &:checked + .time-selector__fields-signs__label-custom {
                    background-color: var(--color-primary-light-2);
                    color: var(--color-main);
                  }
                }
    
                &-custom {
                  display: flex;
                  align-items: center;
                  justify-content: center;
    
                  width: 40px;
                  height: 32px;
    
                  background-color: var(--color-main);
    
                  text-align: center;
                  font-size: 16px;
                  font-weight: 500;
                  color: var(--color-text-main);
    
                  transition: all 0.3s ease-in-out;
                }
              }
            }
          }
    
          &__dials {
            position: relative;
            margin: 0 auto;
    
            width: 220px;
            height: 220px;
            border-radius: 100%;
            background-color: var(--color-main);
    
            &.is-locked {
              opacity: 0.6;
    
              .clock-face {
                pointer-events: none;
              }
            }
    
            & .clock-face {
              position: absolute;
              inset: 0;
              width: 100%;
              height: 100%;
              background-color: var(--color-main);
              border-radius: inherit;
              transform-origin: center center;
    
              &__number {
                --radius: 90px;
    
                position: absolute;
                top: 50%;
                left: 50%;
    
                display: flex;
                align-items: center;
                justify-content: center;
    
                width: 30px;
                height: 30px;
                padding: 2px;
                margin: -15px 0 0 -15px;
    
                border-radius: 50%;
    
                transform:
                  rotate(var(--angle))
                  translateY(calc(var(--radius) * -1))
                  rotate(calc(var(--angle) * -1));
    
                font-size: 16px;
                font-weight: 400;
                color: var(--color-text-main);
    
                &:hover {
                  background-color: var(--color-primary-light-2);
                }
    
                &.active {
                  background-color: var(--color-primary);
                  color: var(--color-main);
                }
    
                &.is-tick {
                  width: 24px;
                  height: 24px;
                  background: transparent;
    
                  &:hover {
                    background: transparent;
                  }
                }
              }
    
              &__pivot {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
    
                z-index: 2;
    
                width: 10px;
                height: 10px;
    
                border-radius: 50%;
                background-color: var(--color-primary);
              }
    
              &__hand {
                --minute-hand-length: 75px;
                --hour-hand-length: 55px;
    
                position: absolute;
                width: 100%;
                height: 100%;
    
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s ease;
    
                &.hour-hand {
                  
                  &::before {
                    height: var(--hour-hand-length);
                    margin-top: calc(var(--hour-hand-length) * -1);
                  }
                }
    
                &.minute-hand {
                  
                  &::before {
                    height: var(--minute-hand-length);
                    margin-top: calc(var(--minute-hand-length) * -1);
                  }
                }
    
                &.is-visible {
                  opacity: 1;
                }
    
                &::before {
                  content: '';
                  position: absolute;
                  top: 50%;
                  left: 50%;
                  
                  width: 3.5px;
                  height: var(--hand-length);
    
                  margin-left: -1px;
                  margin-top: calc(var(--hand-length) * -1);
    
                  background-color: var(--color-primary);
                  border-radius: 3px;
    
                  transform: rotate(var(--angle));
                  transform-origin: bottom center;
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

  .clock-face-anim-enter-active,
  .clock-face-anim-leave-active {
    transition: opacity 0.3s ease, transform 0.3s ease;
  }

  .clock-face-anim-enter-from,
  .clock-face-anim-leave-to {
    opacity: 0;
    transform: scale(0.7);
  }

  .clock-face-anim-enter-to,
  .clock-face-anim-leave-from {
    opacity: 1;
    transform: scale(1);
  }

</style>

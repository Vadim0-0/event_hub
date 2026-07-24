<script setup lang="ts">
  defineOptions({ inheritAttrs: false });

  type InputType = 'text' | 'email' | 'password' | 'search' | 'tel' | 'url' | 'number';

  interface Props {
    type?: InputType
    disabled?: boolean
    label?: string
    placeholder?: string
    id?: string
    class?: string
    name?: string
    inputClass?: string
    errorMessage?: string
    min?: number
    max?: number
    step?: number
  };

  const props = withDefaults(defineProps<Props>(), {
    type: 'text',
    disabled: false,
    label: '',
    placeholder: '',
    id: undefined,
    class: '',
    name: undefined,
    errorMessage: '',
    min: 0,
    max: 100,
    step: 1,
  });

  const modelValue = defineModel<string | number>({ default: '' });

  const hasError = computed(() => Boolean(props.errorMessage?.trim()));
  const isNumberInput = computed(() => props.type === 'number');

  function parseNumber(value: string | number): number | null {
    if (value === '' || value === null || value === undefined) return null;
    const num = typeof value === 'number' ? value : Number(value);
    return Number.isFinite(num) ? num : null;
  };

  function clamp(value: number): number {
    return Math.min(props.max, Math.max(props.min, value));
  };

  function getCurrentNumber(): number {
    return clamp(parseNumber(modelValue.value) ?? props.min);
  };

  function increase() {
    if (props.disabled || !isNumberInput.value) return;
    modelValue.value = clamp(getCurrentNumber() + props.step);
  };

  function decrease() {
    if (props.disabled || !isNumberInput.value) return;
    modelValue.value = clamp(getCurrentNumber() - props.step);
  };

  const canIncrease = computed(() =>
    isNumberInput.value && getCurrentNumber() + props.step <= props.max,
  );

  const canDecrease = computed(() =>
    isNumberInput.value && getCurrentNumber() - props.step >= props.min,
  );

  function onNumberInput(event: Event) {
    if (!isNumberInput.value) return;

    const num = parseNumber((event.target as HTMLInputElement).value);
    if (num === null) return;

    if (num > props.max) {
      modelValue.value = props.max
    };
  };

  function onNumberBlur() {
    if (!isNumberInput.value) return;

    const num = parseNumber(modelValue.value);

    if (num === null) {
      modelValue.value = '';
      return;
    };

    modelValue.value = clamp(num);
  }

</script>

<template>
  <label
    :class="[ props.class, { error: hasError }]"
    :for="props.id"
    class="
      ui-input
    "
  >
    <span class="ui-input__label" v-if="props.label">{{ props.label }}</span>
    <div class="ui-input__field">
      <input
        :id="props.id"
        :name="props.name"
        :type="props.type"
        :disabled="props.disabled"
        :placeholder="props.placeholder"
        :class="[
          props.inputClass,
          { 'ui-input__field-input--number': isNumberInput },
        ]"
        :min="isNumberInput ? props.min : undefined"
        :max="isNumberInput ? props.max : undefined"
        :step="isNumberInput ? props.step : undefined"
        v-model="modelValue"
        @input="onNumberInput"
        @blur="onNumberBlur"
        v-bind="$attrs"
      />
      <div 
        v-if="isNumberInput"
        class="ui-input__field-control"
      >
        <button
          type="button"
          class="ui-input__field-control__btn"
          :disabled="props.disabled || !canIncrease"
          @click="increase"
        >
          <Icon name="eva:arrow-up-fill" mode="svg" />
        </button>
        <button
          type="button"
          class="ui-input__field-control__btn minus-btn"
          :disabled="props.disabled || !canDecrease"
          @click="decrease"
        >
          <Icon name="eva:arrow-up-fill" mode="svg" />
        </button>
      </div>
    </div>
    <p v-if="hasError" class="ui-input__error">
      {{ props.errorMessage }}
    </p>
  </label>
</template>

<style lang="scss">

  .ui-input {
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

    &__field {
      position: relative;
      width: 100%;

      & input {
        padding: 16px 12px;
        width: 100%;
        outline: none;
        border: none;
        box-shadow: none;
        background-color: var(--color-third);
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

      &-control {
        position: absolute;
        top: 50%;
        right: 5px;
        transform: translateY(-50%);

        display: flex;
        flex-direction: column;
        gap: 3px;

        transition: opacity 0.3s ease-in-out;
        opacity: 0;

        &__btn {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 16px;
          height: 16px;

          border-radius: 2px;
          background-color: var(--color-primary-light-2);

          & svg {
            color: var(--color-main);
          }

          &.minus-btn {
            transform: rotate(180deg);
          }

          &:hover {
            background-color: var(--color-primary);
          }
        }


      }

      &:hover {
        & .ui-input__field-control {
          opacity: 1;
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

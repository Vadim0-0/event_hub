<script setup lang="ts">

  defineOptions({ inheritAttrs: false });

  interface Props {
    label?: string
    id?: string
    class?: string
    disabled?: boolean
    errorMessage?: string
    inputClass?: string
    length?: number;
  };

  const props = withDefaults(defineProps<Props>(), {
    label: '',
    id: undefined,
    class: '',
    disabled: false,
    errorMessage: '',
    length: 6,
  });

  const modelValue = defineModel<string>({ default: '' });
  const hasError = computed(() => Boolean(props.errorMessage?.trim()));

  const digits = ref<string[]>([]);
  const inputsRef = ref<HTMLInputElement[]>([]);

  function resetDigits(code = '') {
    const size = props.length;
    const chars = code.replace(/\D/g, '').slice(0, size).split('');
    digits.value = Array.from({ length: size }, (_, i) => chars[i] ?? '');
    inputsRef.value = [];
  };

  function setInputRef(el: Element | ComponentPublicInstance | null, index: number) {
    if (el) inputsRef.value[index] = el as HTMLInputElement;
  };

  function focusAt(index: number) {
    inputsRef.value[index]?.focus();
    inputsRef.value[index]?.select();
  };

  function onInput(index: number, event: Event) {
    const input = event.target as HTMLInputElement;
    const digit = input.value.replace(/\D/g, '').slice(-1);

    digits.value[index] = digit;
    input.value = digit;

    if (digit && index < props.length - 1) {
      focusAt(index + 1);
    };
  };

  function onKeydown(index: number, event: KeyboardEvent) {
    if (event.key !== 'Backspace') return;

    if (digits.value[index]) {
      digits.value[index] = '';
      return;
    };

    if (index > 0) {
      event.preventDefault();
      digits.value[index - 1] = '';
      focusAt(index - 1);
    };
  };

  function onPaste(event: ClipboardEvent) {
    event.preventDefault();
    const text = event.clipboardData?.getData('text') ?? '';
    const onlyDigits = text.replace(/\D/g, '').slice(0, props.length).split('');

    for (let i = 0; i < props.length; i++) {
      digits.value[i] = onlyDigits[i] ?? '';
    };

    const next = Math.min(onlyDigits.length, props.length - 1);
    focusAt(next);
  };

  watch(
    () => [props.length, modelValue.value] as const,
    ([, code]) => {
      const joined = digits.value.join('')
      if (code === joined && digits.value.length === props.length) return
      resetDigits(code)
    },
    { immediate: true },
  );

  watch(digits, (value) => {
    modelValue.value = value.join('')
  }, { deep: true });


</script>

<template>
  <label 
    class="ui-verification"
    :class="[props.class, { error: hasError }]"
    :for="props.id"
  >
    <span v-if="props.label" class="ui-verification__label">
      {{ props.label }}
    </span>

    <div class="ui-verification__fields">
      <input
        v-for="(_, index) in props.length"
        :key="`${props.length}-${index}`"
        :id="index === 0 ? props.id : undefined"
        :ref="(el) => setInputRef(el, index)"
        type="text"
        inputmode="numeric"
        maxlength="1"
        autocomplete="one-time-code"
        :disabled="props.disabled"
        :value="digits[index]"
        @input="onInput(index, $event)"
        @keydown="onKeydown(index, $event)"
        @paste="onPaste($event)"
        :class="props.inputClass"
      >
    </div>

    <p v-if="hasError" class="ui-verification__error">
      {{ props.errorMessage }}
    </p>
  </label>
</template>

<style lang="scss">

  .ui-verification{
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

    &__fields {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      width: 100%;

      & input {
        padding: 14px 10px;
        width: 100%;
        outline: none;
        border: 1px solid var(--color-third);
        box-shadow: none;
        background-color: var(--color-third);
        border-radius: 5px;
        transition: all 0.3s ease-in-out;
  
        text-align: center;
        color: var(--color-text-main);
        font-size: 32px;
  
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

        &:hover {
          // background-color: var(--color-primary-light-2) !important;
        }
  
        &:disabled {
          opacity: 0.6;
          cursor: not-allowed;
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

<script setup lang="ts">
// Reusable text field with default props, v-model, and attrs forwarding.
defineOptions({ inheritAttrs: false })

type InputType = 'text' | 'email' | 'password' | 'search' | 'tel' | 'url' | 'number'

interface Props {
  type?: InputType
  disabled?: boolean
  label?: string
  placeholder?: string
  id?: string
  class?: string
  name?: string
  inputClass?: string
  /** Текст ошибки; пустая строка — без ошибки */
  errorMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  label: '',
  placeholder: '',
  id: undefined,
  class: '',
  name: undefined,
  errorMessage: '',
})

const modelValue = defineModel<string>({ default: '' })

const hasError = computed(() => Boolean(props.errorMessage?.trim()))
</script>

<template>
  <label
    :class="[ props.class, { error: hasError }]"
    :for="props.id"
    class="
      ui-input
    "
  >
    <span v-if="props.label">{{ props.label }}</span>
    <input
      :id="props.id"
      :name="props.name"
      :type="props.type"
      :disabled="props.disabled"
      :placeholder="props.placeholder"
      :class="props.inputClass"
      v-model="modelValue"
      v-bind="$attrs"
    />
    <p v-if="hasError" class="ui-input__error">
      {{ props.errorMessage }}
    </p>
  </label>
</template>

<style lang="scss">

  .ui-input {
    width: 100%;
    outline: none;
    border: none;

    & input {
      padding: 16px 12px;
      width: 100%;
      outline: none;
      border: none;
      box-shadow: none;
      background-color: var(--color-secondary);
      transition: all 0.3s ease-in-out;

      color: var(--color-text-main);
      font-size: var(--text-body-xl);

      &:focus {
        outline: none;
        border-color: var(--color-primary-hover);
        
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

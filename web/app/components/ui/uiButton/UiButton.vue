<script setup lang="ts">
// Reusable UI control with default props and attrs forwarding.
type ButtonType = 'button' | 'submit' | 'reset'

interface Props {
  type?: ButtonType
  disabled?: boolean
  label?: string
  id?: string
  class?: string
  styleType?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'button',
  disabled: false,
  label: '',
  id: undefined,
  class: '',
  styleType: 'primary',
})
</script>

<template>
  <button
    :class="['ui-btn', `ui-btn--${props.styleType}`, props.class]"
    :id="props.id"
    :type="props.type"
    :disabled="props.disabled"
    v-bind="$attrs"
    
  >
  <slot />
</button>
</template>

<style lang="scss">
  .ui-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;

    padding: 6px 8px;
    border-radius: 6px;
    border: 1px solid var(--color-fifth);
    background-color: var(--color-secondary);

    font-size: var(--text-body-sm);
    font-weight: 600;
    color: var(--color-text-main);

    &:hover {
      background-color: var(--color-primary-light);
    }
  }
</style>
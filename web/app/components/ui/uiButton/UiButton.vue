<script setup lang="ts">
  import type { HTMLAttributes } from 'vue';

  type ButtonType = 'button' | 'submit' | 'reset';
  type ButtonStyle = 'primary' | 'delete' | 'cancel';

  interface Props {
    type?: ButtonType
    disabled?: boolean
    label?: string
    id?: string
    class?: HTMLAttributes['class']
    styleType?: ButtonStyle
  }

  const props = withDefaults(defineProps<Props>(), {
    type: 'button',
    disabled: false,
    label: '',
    id: undefined,
    class: '',
    styleType: 'primary',
  });
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
      background-color: var(--color-third);
    }

    &--primary {
      border-color: var(--color-primary);
      background-color: var(--color-primary);
      color: var(--color-main);

      &:hover {
        border-color: var(--color-primary-hover);
        background-color: var(--color-primary-hover);
        color: var(--color-main);

        & svg {
          color: var(--color-main);
        }
      }
    }

    &--delete {
      border-color: var(--color-error);
      background-color: #ffcccc;
      color: var(--color-error);

      &:hover {
        background-color: #ffa2a2;
        color: var(--color-error);

        & svg {
          color: var(--color-error);
        }
      }
    }

    &:disabled {
      opacity: 0.7;
      pointer-events: none;
    }
  }

  @media (max-width: 767px) {
    .ui-btn {
      font-weight: 500;
    }
  }
</style>
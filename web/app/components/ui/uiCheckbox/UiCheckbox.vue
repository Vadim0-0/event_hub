<script setup lang="ts">
  defineOptions({ inheritAttrs: false });

  interface Props {
    disabled?: boolean
    label?: string
    id?: string
    class?: string
    name?: string
    errorMessage?: string
  };

  const props = withDefaults(defineProps<Props>(), {
    disabled: false,
    label: '',
    id: undefined,
    class: '',
    name: undefined,
    errorMessage: '',
  });

  const modelValue = defineModel<boolean>({ default: false });

  const hasError = computed(() => Boolean(props.errorMessage?.trim()));
</script>

<template>
  <label 
    :for="id"
    class="ui-checkbox"
    :class="[props.class, { error: hasError }]"
  >
    <div class="ui-checkbox__info">
      <div class="custom-checkbox">
        <input 
          :id="id"
          :name="props.name"
          type="checkbox"
          :disabled="props.disabled"
          v-model="modelValue"
          v-bind="$attrs"
        >
        <span aria-hidden="true"></span>
      </div>
      <p v-if="props.label">
        {{ props.label }}
      </p>
    </div>
    <p v-if="hasError" class="ui-checkbox__error"> {{ props.errorMessage }} </p>
  </label>
</template>

<style scoped lang="scss">
  .ui-checkbox {
    display: flex;
    flex-direction: column;
    cursor: pointer;

    &__info {
      display: flex;
      align-items: start;
      gap: 10px;

      & .custom-checkbox {
        position: relative;

        & input {
          position: absolute;
          top: 0;
          left: 0;
          width: 0;
          height: 0;
          opacity: 0;
          visibility: hidden;
          pointer-events: none;

          &:checked + span {

            &::after {
              opacity: 1;
            }
          }
        }

        & span {
          position: relative;
          display: block;
          flex-shrink: 0;
          margin-top: 2px;
          width: 22px;
          height: 22px;

          border-radius: 3px;
          border: 1px solid var(--color-fifth);
          background-color: var(--color-secondary);

          &::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: calc(100% - 4px);
            height: calc(100% - 4px);
            background-color: var(--color-primary);
            border-radius: inherit;
            opacity: 0;
            transition: opacity 0.1s ease-in-out;
          }
        }
      }

      & p {
        font-size: 18px;
        font-weight: 500;
        color: var(--color-text-main);
      }
    }

    &__error {
      margin-top: 10px;
      font-weight: 500;
      font-size: 18px;
      color: var(--color-error);
    }
  }
</style>

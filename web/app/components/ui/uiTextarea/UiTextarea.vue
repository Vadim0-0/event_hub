<script setup lang="ts">
  defineOptions({ inheritAttrs: false });

  interface Props {
    disabled?: boolean
    label?: string
    placeholder?: string
    id?: string
    class?: string
    name?: string
    inputClass?: string
    errorMessage?: string
    rows?: number
    minHeight?: number
    maxHeight?: number
  };

  const props = withDefaults(defineProps<Props>(), {
    disabled: false,
    label: '',
    placeholder: '',
    id: undefined,
    class: '',
    name: undefined,
    inputClass: '',
    errorMessage: '',
    rows: 4,
    minHeight: 120,
    maxHeight: 400,
  });

  const modelValue = defineModel<string>({ default: '' });

  const hasError = computed(() => Boolean(props.errorMessage?.trim()));

  // Custom Resize
  const fieldRef = ref<HTMLElement | null>(null);
  const height = ref(props.minHeight);

  function startResize(event: MouseEvent) {
    if (props.disabled) return;

    const textarea = fieldRef.value?.querySelector('textarea');
    if (!textarea) return;

    const startY = event.clientY;
    const startHeight = textarea.offsetHeight;

    const onMouseMove = (moveEvent: MouseEvent) => {
      const nextHeight = startHeight + (moveEvent.clientY - startY);

      height.value = Math.min(
        props.maxHeight,
        Math.max(props.minHeight, nextHeight),
      );
    };

    const onMouseUp = () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
  };

</script>

<template>
  <label
    :for="props.id"
    :class="[ props.class, { error: hasError }]"
    class="
      ui-textarea
    "
  >
    <span class="ui-textarea__label" v-if="props.label">{{ props.label }}</span>
    <div ref="fieldRef" class="ui-textarea__field">
      <textarea
        :id="props.id"
        :name="props.name"
        :rows="props.rows"
        :disabled="props.disabled"
        :placeholder="props.placeholder"
        :class="props.inputClass"
        :style="{ height: `${height}px` }"
        v-model="modelValue"
        v-bind="$attrs"
        data-lenis-prevent
      />
      <span 
        class="ui-textarea__field-resize"
        @mousedown.prevent="startResize"
      ></span>
    </div>
    <p v-if="hasError" class="ui-input__error">
      {{ props.errorMessage }}
    </p>
  </label>
</template>

<style lang="scss">

  .ui-textarea {
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

      & textarea {
        padding: 16px 12px;
        width: 100%;
        outline: none;
        border: 1px solid var(--color-third);
        box-shadow: none;
        background-color: var(--color-third);
        border-radius: 5px;
  
        color: var(--color-text-main);
        font-size: var(--text-body-xl);

        resize: none; 
  
        &:focus {
          outline: none;
          // border-color: var(--color-primary-hover);
        }

        &:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
      }

      &-resize {
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);

        width: 50%;
        height: 4px;

        border-radius: 2px;
        background-color: var(--color-primary-light-2);

        cursor: ns-resize;
        user-select: none;
        touch-action: none;

        transition: background-color 0.3s ease-in-out;

        &:hover {
          background-color: var(--color-primary);
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

      & textarea {
        color: var(--color-error) !important;
        border-color: var(--color-error) !important;
      }
    }
  }

</style>

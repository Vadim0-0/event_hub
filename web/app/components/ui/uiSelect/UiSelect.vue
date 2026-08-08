<script setup lang="ts">

  defineOptions({ inheritAttrs: false });

  type SelectStyle = 'normal' | 'collapsed';

  export type SelectOptionLabel =
  | string
  | { normal: string; collapsed: string }

  // === Types ===
  interface SelectOption {
    value: string
    label: SelectOptionLabel
  };

  interface Props {
    options?: SelectOption[]
    disabled?: boolean
    label?: string
    placeholder?: string
    id?: string
    class?: string
    name?: string
    errorMessage?: string
    styleType?: SelectStyle
  };


  // === Props & model ===
  const props = withDefaults(defineProps<Props>(), {
    options: () => [],
    disabled: false,
    label: '',
    placeholder: 'Select',
    id: undefined,
    class: '',
    name: undefined,
    errorMessage: '',
    styleType: 'normal',
  });

  const modelValue = defineModel<string>({ default: '' });

  function getOptionLabel(
    label: SelectOptionLabel,
    style: SelectStyle = 'normal',
  ): string {
    if (typeof label === 'string') return label
    return style === 'collapsed' ? label.collapsed : label.normal
  };


  // === Локальный state ===
  const isOpen = ref(false);
  const contentRef = ref<HTMLElement | null>(null);


  // === Computed ===
  const hasError = computed(() => Boolean(props.errorMessage?.trim()));

  const selectedLabel = computed(() => {
    const option = props.options.find((item) => item.value === modelValue.value);
    if (!option) return props.placeholder;
    return getOptionLabel(option.label, props.styleType);
  });


  // === Handlers ===
  function toggleDropdown() {
    if (props.disabled) return;
    isOpen.value = !isOpen.value;
  };

  function selectOption(option: SelectOption) {
    modelValue.value = option.value;
    isOpen.value = false;
  };

  function handleClickOutside(event: MouseEvent) {
    if (!isOpen.value) return;
    const target = event.target as Node | null;
    if (contentRef.value && target && !contentRef.value.contains(target)) {
      isOpen.value = false;
    };
  };


  // === Lifecycle ===
  onMounted(() => {
    document.addEventListener('click', handleClickOutside);
  });
  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside);
  });
  
</script>

<template>
  <label
    :class="[props.class, `ui-select--${props.styleType}`, { error: hasError }]"
    :for="props.id"
    class="ui-select"
  >

    <span v-if="props.label" class="ui-select__label">
      {{ props.label }}
    </span>

    <div ref="contentRef" class="ui-select__content">
      <button
        type="button"
        class="ui-select__content-btn"
        :class="{ active: isOpen }"
        :disabled="props.disabled"
        @click="toggleDropdown"
      >
        <p>{{ selectedLabel }}</p>
        <span class="ui-select__content-btn__arrow">
          <Icon name="ep:arrow-up-bold" mode="svg" />
        </span>
      </button>
  
      <ul :class="{ active: isOpen }" data-lenis-prevent>
        <li v-for="option in props.options" :key="option.value">
          <button 
            type="button" 
            :class="{ choose: modelValue === option.value }"
            @click="selectOption(option)"
          >
              {{ getOptionLabel(option.label, props.styleType) }}
          </button>
        </li>
      </ul>
  
      <select
        :id="props.id"
        :name="props.name"
        v-model="modelValue"
        :disabled="props.disabled"
        tabindex="-1"
        aria-hidden="true"
      >
        <option v-if="!modelValue" disabled value="">
          {{ props.placeholder }}
        </option>
        <option
          v-for="option in props.options"
          :key="option.value"
          :value="option.value"
        >
          {{ option.label }}
        </option>
      </select>
    </div>

    <div v-if="hasError" class="ui-select__error">
      <p>
        {{ props.errorMessage }}
      </p>
    </div>
  </label>
</template>

<style lang="scss">
  
  .ui-select {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    width: 100%;

    z-index: 5;

    &__label {
      padding: 0 5px;
      margin-bottom: 1px;
      color: var(--color-text-main);
      font-size: var(--text-body-sm);
      font-weight: 500;
    }

    &__content {
      position: relative;
      width: 100%;

      &-btn {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 5px;

        padding: 6px 8px;
        width: 100%;

        background-color: var(--color-main);
        border: 1px solid var(--color-fifth);
        border-radius: 5px;

        z-index: 2;

        color: var(--color-text-main);
        font-size: var(--text-body-sm);
        font-weight: 600;

        & p {
          white-space: nowrap;
          overflow: hidden;
        }

        &__arrow {
          display: flex;
          align-items: center;
          justify-content: center;
          transform: rotate(180deg);
          transition: transform 0.3s ease-in-out;

          & svg {
            width: 100%;
            height: 100%;
          }
        }

        &:hover {
          background-color: var(--color-primary-light);
        }

        &.active {
          border-radius: 5px 5px 0 0;

          & .ui-select__content-btn__arrow {
            transform: rotate(0);
          }
        }
      }

      & ul {
        position: absolute;
        top: 100%;
        left: 0;

        display: flex;
        flex-direction: column;
        overflow-y: auto;
        width: 100%;
        max-height: 300px;

        background-color: var(--color-main);
        border: 1px solid var(--color-fifth);
        border-top: none;
        border-radius: 0 0 5px 5px;
        box-shadow: 0px 6px 15px -1px rgba(33, 33, 33, 0.1);

        transition: all 0.3s ease-in-out;
        opacity: 0;
        transform: translateY(-20px);
        pointer-events: none;
        visibility: hidden;

        z-index: 1;

        &.active {
          opacity: 1;
          transform: translateY(0);
          pointer-events: all;
          visibility: visible;
        }

        & li {
          width: 100%;

          & button {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 5px;

            padding: 6px 8px;
            width: 100%;

            color: var(--color-text-main);
            font-size: var(--text-body-sm);
            font-weight: 600;
            background-color: var(--color-main);

            &:hover {
              background-color: var(--color-primary-light);
            }

            &.choose {
              background-color: var(--color-primary);
              color: var(--color-main);
            }
          }
        }
      }

      & select {
        position: absolute;
        top: 0;
        left: 0;
        width: 0;
        height: 0;
        pointer-events: none;
        visibility: hidden;
        opacity: 0;
      }
    }

    &--collapsed {

      & .ui-select__content {

        &-btn {
          padding: 5px 5px;

          &__arrow {
            width: 15px;
            height: 15px;
          }
        }
      }
    }
  }

</style>
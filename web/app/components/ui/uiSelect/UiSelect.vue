<script setup lang="ts">

  defineOptions({ inheritAttrs: false });

  type SelectStyle = 'normal' | 'collapsed';

  type ListLayout = 'bottom' | 'top';

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

    buttonStyle?: string

    listLayout?: ListLayout
    listStyle?: string
    listButtonStyle?: string

    searchVisible?: boolean
    searchPlaceholder?: string
    searchStyle?: string
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

    buttonStyle: '',

    listLayout: 'bottom',
    listStyle: '',
    listButtonStyle: '',

    searchVisible: false,
    searchPlaceholder: 'Search...',
    searchStyle: '',
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
  const searchQuery = ref('');


  // === Computed ===
  const hasError = computed(() => Boolean(props.errorMessage?.trim()));

  const selectedLabel = computed(() => {
    const option = props.options.find((item) => item.value === modelValue.value);
    if (!option) return props.placeholder;
    return getOptionLabel(option.label, props.styleType);
  });

  const filteredOptions = computed(() => {
    if (!props.searchVisible || !searchQuery.value.trim()) {
      return props.options;
    }

    const query = searchQuery.value.trim().toLowerCase();

    return props.options.filter((option) => {
      const label = getOptionLabel(option.label, props.styleType).toLowerCase();
      const value = option.value.toLowerCase();
      return label.includes(query) || value.includes(query);
    });
  });


  // === Handlers ===
  function toggleDropdown() {
    if (props.disabled) return;
    isOpen.value = !isOpen.value;

    if (!isOpen.value) {
      searchQuery.value = '';
    };
  };

  function selectOption(option: SelectOption) {
    modelValue.value = option.value;
    isOpen.value = false;
    searchQuery.value = '';
  };

  function handleClickOutside(event: MouseEvent) {
    if (!isOpen.value) return;
    const target = event.target as Node | null;
    if (contentRef.value && target && !contentRef.value.contains(target)) {
      isOpen.value = false;
      searchQuery.value = '';
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
    :class="[props.class, `ui-select--${props.styleType}`, { error: hasError }, `list-${listLayout}`]"
    :for="props.id"
    class="ui-select"
  >

    <span v-if="props.label" class="ui-select__label">
      {{ props.label }}
    </span>

    <div 
      ref="contentRef" 
      class="ui-select__content"
    >
      <button
        type="button"
        class="ui-select__content-btn"
        :class="[props.buttonStyle, { active: isOpen }]"
        :disabled="props.disabled"
        @click="toggleDropdown"
      >
        <p>{{ selectedLabel }}</p>
        <span class="ui-select__content-btn__arrow">
          <Icon name="ep:arrow-up-bold" mode="svg" />
        </span>
      </button>
  
      <ul :class="[props.listStyle, {active: isOpen} ]" data-lenis-prevent >
        <li v-if="searchVisible" class="item-search">
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            :placeholder="searchPlaceholder"
            :class="searchStyle"
            @click.stop
            @keydown.stop
          />
        </li>
        <li v-for="option in filteredOptions" :key="option.value">
          <button 
            type="button" 
            :class="[props.listButtonStyle, { choose: modelValue === option.value }]"
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
        font-weight: 500;

        & p {
          white-space: nowrap;
          overflow: hidden;
        }

        &__arrow {
          display: flex;
          align-items: center;
          justify-content: center;
          transition: transform 0.3s ease-in-out;

          & svg {
            width: 100%;
            height: 100%;
          }
        }

        &:hover {
          background-color: var(--color-primary-light);
        }
      }

      & ul {
        position: absolute;
        left: 0;

        display: flex;
        flex-direction: column;
        overflow-y: auto;
        width: 100%;
        max-height: 300px;

        background-color: var(--color-main);
        border: 1px solid var(--color-fifth);

        transition: all 0.3s ease-in-out;
        opacity: 0;
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

          &.item-search {
            position: sticky;
            top: 0;
            z-index: 1;

            & input {
              display: flex;
              align-items: center;
              justify-content: space-between;
              gap: 5px;

              padding: 6px 8px;
              width: 100%;

              color: var(--color-text-main);
              font-size: var(--text-body-sm);
              font-weight: 500;
              background-color: var(--color-third);

              &::placeholder {
                font-size: var(--text-body-sm);
                font-weight: 500;
              }

              &.choose {
                background-color: var(--color-primary);
                color: var(--color-main);
              }
            }
          }

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
            font-weight: 500;
            // background-color: var(--color-main);

            &:hover {
              background-color: var(--color-primary-hover);
              color: var(--color-main);
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


    &.list-top {
      
      & .ui-select__content {

        &-btn {

          &__arrow {
            transform: rotate(0);
          }

          &.active {
            border-radius: 0 0 5px 5px;

            & .ui-select__content-btn__arrow {
              transform: rotate(180deg);
            }
          }
        }
        
        & ul {
          bottom: 100%;
          transform: translateY(20px);

          border-radius: 5px 5px 0 0;
          border-bottom: none;
          box-shadow: 0px -2px 15px -1px rgba(33, 33, 33, 0.1);

          &.active {
            transform: translateY(0);
          }
        }
      }
    }

    &.list-bottom {

      & .ui-select__content {

        &-btn {

          &__arrow {
            transform: rotate(180deg);
          }

          &.active {
            border-radius: 5px 5px 0 0;

            & .ui-select__content-btn__arrow {
              transform: rotate(0);
            }
          }
        }
        
        & ul {
          top: 100%;
          transform: translateY(-20px);

          border-radius: 0 0 5px 5px;
          border-top: none;
          box-shadow: 0px 6px 15px -1px rgba(33, 33, 33, 0.1);

          &.active {
            transform: translateY(0);
          }
        }
      }
    }
  }

  @media (max-width: 767px) {
    .ui-select {

      &--collapsed {

        & .ui-select__content {

          &-btn {
            padding: 5px 3px;

            &__arrow {
              width: 12px;
              height: 12px;
            }
          }
        }
      }
    }
  }

</style>
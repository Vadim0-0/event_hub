<script setup lang="ts">
  import chatSettingsRaw from '~~/data/components/chatSettings.json';
  import { mapChatSettings } from '~/mappers/components/chatSettings';
  import type { ChatSettingsRaw } from '~/types/i18n/components/chatSettings';

  const { locale } = useI18n();
  const content = computed(() =>
    mapChatSettings((chatSettingsRaw as ChatSettingsRaw[])[0]!, locale.value),
  );

  const emit = defineEmits<{
    clearHistory: [];
    deleteChat: [];
  }>();

  const chatSettingsButton = computed(() => content.value.chatSettingsButton);

  function onAction(type: 'clearHistory' | 'deleteChat') {
    if (type === 'clearHistory') {
      emit('clearHistory');
    } else {
      emit('deleteChat');
    }
  }


</script>

<template>
  <ul class="
      flex flex-col
      w-full p-1
      bg-main rounded-sm shadow-[0px_6px_15px_-1px_rgba(33,33,33,0.1)]
    "
  >
    <li v-for="item, index in chatSettingsButton" :key=item.type>
      <button 
        class="
          flex items-center justify-center gap-2
          p-2 w-full
          rounded-sm
        "
        :class="[item.isDelete ? 'hover:bg-[#FECACA]' : 'hover:bg-primary-light']"
        @click="onAction(item.type)"
      >
        <Icon :name="item.icon" mode="svg" 
          class="size-5 shrink-0"
          :class="[item.isDelete ? 'text-error' : 'text-text-main']"
        />
        <p class="whitespace-nowrap text-body-sm"
          :class="[item.isDelete ? 'text-error' : 'text-text-main']"
        >
          {{ item.text }}
        </p>
      </button>
    </li>
  </ul>
</template>

<style scoped lang="scss">

</style>
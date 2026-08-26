<script setup lang="ts">

  import type { Message } from '~/types/domain/messaging';
  import conversationChatRaw from '~~/data/components/ui/conversationChat.json';
  import { mapConversationChat } from '~/mappers/components/ui/conversationChat';
  import type { ConversationChatRaw } from '~/types/i18n/components/ui/conversationChat';

  const { locale } = useI18n();
  const content = computed(() =>
    mapConversationChat((conversationChatRaw as ConversationChatRaw[])[0]!, locale.value),
  );

  const props = defineProps<{
    messages: Message[]
    currentUserId: number
    loading?: boolean
    loadingOlder?: boolean
    hasMore?: boolean 
  }>();

  const dayjs = useDayjs();

  type ChatItem =
    | { type: 'date'; key: string; label: string }
    | { type: 'message'; key: string; message: Message }
  
  function formatMessageTime(iso: string) {
    return dayjs(iso).format('HH:mm')
  };

  function formatDateLabel(iso: string) {
    const d = dayjs(iso);
    const today = dayjs();

    if (d.isSame(today, 'day')) return content.value.today;
    if (d.isSame(today.subtract(1, 'day'), 'day')) return content.value.yesterday;

    return d.locale(locale.value).format('DD MMMM YYYY');
  };

  const chatItems = computed<ChatItem[]>(() => {
    const items: ChatItem[] = [];
    let lastDate = '';

    for (const message of props.messages) {
      const dateKey = dayjs(message.created_at).format('YYYY-MM-DD')

      if (dateKey !== lastDate) {
        items.push({
          type: 'date',
          key: `date-${dateKey}`,
          label: formatDateLabel(message.created_at),
        });
        lastDate = dateKey;
      };

      items.push({
        type: 'message',
        key: message.id,
        message,
      });
    };

    return items
  });

</script>

<template>
  <div 
    class="
      flex flex-col gap-2 p-5
      max-sm:gap-1 max-sm:p-2
    "
  >
    <p
      v-if="loadingOlder"
      class="text-text-secondary text-sm text-center py-2 max-sm:p-1"
    >
      {{ content.loadingOlderMessages }}
    </p>
    <p
      v-else-if="hasMore === false && chatItems.length"
      class="text-text-secondary text-sm text-center py-2 max-sm:p-1"
    >
      {{ content.beginningOfConversation }}
    </p>
    <p v-if="loading" class="text-text-secondary text-sm text-center">
      {{ content.loadingMessages }}
    </p>
    <p
      v-else-if="!chatItems.length"
      class="text-text-secondary text-sm text-center"
    >
      {{ content.noMessages }}
    </p>
    
    <template v-else>
      <template v-for="item in chatItems" :key="item.key">
        <ChatDateDivider
          v-if="item.type === 'date'"
          :label="item.label"
        />
        <ChatMessage
          v-else
          :body="item.message.body"
          :is-mine="item.message.sender_id === currentUserId"
          :time="formatMessageTime(item.message.created_at)"
        />
      </template>
    </template>
  </div>
</template>

<style scoped lang="scss">

</style>
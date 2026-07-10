<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'
import MessageBubble from './MessageBubble.vue'

const { messages } = storeToRefs(useChatStore())
const scrollEl = ref<HTMLElement | null>(null)

// 深層監聽:新訊息 push、串流逐字追加 content,都要跟著捲到底
watch(
  messages,
  async () => {
    await nextTick()
    scrollEl.value?.scrollTo({ top: scrollEl.value.scrollHeight })
  },
  { deep: true },
)
</script>

<template>
  <div ref="scrollEl" class="chat-scroll flex-1 overflow-y-auto px-6 py-6">
    <div class="mx-auto flex max-w-3xl flex-col gap-5">
      <MessageBubble v-for="m in messages" :key="m.id" :message="m" />
    </div>
  </div>
</template>

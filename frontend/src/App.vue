<script setup lang="ts">
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from './stores/chat'
import ChatWindow from './components/ChatWindow.vue'
import MessageInput from './components/MessageInput.vue'
import AgentTracePanel from './components/AgentTracePanel.vue'

const { isStreaming } = storeToRefs(useChatStore())

// 手機版:Agent 過程側欄改為滑出式抽屜
const showTrace = ref(false)
</script>

<template>
  <div class="flex h-full flex-col">
    <!-- 頂欄 -->
    <header class="flex items-center gap-3 border-b border-line bg-surface-panel px-4 py-3.5 md:px-6">
      <div class="h-8 w-8 rounded-lg bg-accent/20 flex items-center justify-center">📦</div>
      <div class="min-w-0">
        <h1 class="text-sm font-semibold text-slate-100">訂單管家 AI</h1>
        <p class="truncate text-xs text-slate-500">Order Agent · 生產訂單智慧助手</p>
      </div>
      <div class="ml-auto hidden items-center gap-1.5 text-xs text-slate-500 sm:flex">
        <span class="h-2 w-2 rounded-full bg-emerald-400" />
        已連線
      </div>
      <!-- 手機:開啟 Agent 過程抽屜(串流中發光提示) -->
      <button
        class="ml-auto h-9 w-9 rounded-lg bg-surface-raised text-base flex items-center justify-center sm:ml-0 md:hidden"
        :class="isStreaming ? 'ring-1 ring-accent animate-pulse' : ''"
        aria-label="開啟 Agent 過程"
        @click="showTrace = true"
      >
        🧠
      </button>
    </header>

    <!-- 主體:左聊天、右 Agent 過程 -->
    <div class="flex min-h-0 flex-1">
      <main class="flex min-w-0 flex-1 flex-col">
        <ChatWindow />
        <MessageInput />
      </main>

      <!-- 手機抽屜的背景遮罩 -->
      <div
        v-if="showTrace"
        class="fixed inset-0 z-40 bg-black/50 md:hidden"
        @click="showTrace = false"
      />
      <AgentTracePanel :open="showTrace" @close="showTrace = false" />
    </div>
  </div>
</template>

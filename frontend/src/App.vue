<script setup lang="ts">
import ChatWindow from './components/ChatWindow.vue'
import MessageInput from './components/MessageInput.vue'
import AgentTracePanel from './components/AgentTracePanel.vue'
</script>

<template>
  <div class="flex h-full flex-col">
    <!-- 頂欄 -->
    <header class="flex items-center gap-3 border-b border-line bg-surface-panel px-6 py-3.5">
      <div class="h-8 w-8 rounded-lg bg-accent/20 flex items-center justify-center">📦</div>
      <div>
        <h1 class="text-sm font-semibold text-slate-100">訂單管家 AI</h1>
        <p class="text-xs text-slate-500">Order Agent · 生產訂單智慧助手</p>
      </div>
      <div class="ml-auto flex items-center gap-1.5 text-xs text-slate-500">
        <span class="h-2 w-2 rounded-full bg-emerald-400" />
        已連線
      </div>
    </header>

    <!-- 主體:左聊天、右 Agent 過程 -->
    <div class="flex min-h-0 flex-1">
      <main class="flex min-w-0 flex-1 flex-col">
        <ChatWindow />
        <MessageInput />
      </main>
      <AgentTracePanel />
    </div>
  </div>
</template>

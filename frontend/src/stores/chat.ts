import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { ChatMessage } from '@/types/chat'
import { streamChat } from '@/api/agent'
import { useTraceStore } from '@/stores/trace'

let seq = 0
const nextId = () => `msg_${++seq}`

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([
    {
      id: nextId(),
      role: 'assistant',
      content:
        '你好,我是訂單管家 👋\n可以問我訂單狀況、銷售統計,或請我標記延誤訂單。',
      status: 'done',
    },
  ])
  const sessionId = ref(`s_${Date.now()}`)
  let controller: AbortController | null = null

  // 有任何一則訊息在串流中,輸入框就該鎖住
  const isStreaming = computed(() => messages.value.some((m) => m.status === 'streaming'))

  async function sendMessage(text: string) {
    const trimmed = text.trim()
    if (!trimmed || isStreaming.value) return

    messages.value.push({ id: nextId(), role: 'user', content: trimmed, status: 'done' })

    // 先放一則空的 assistant 訊息,再讓它「長大」——
    // 注意要從陣列尾端取回 reactive proxy,直接改剛剛的字面量物件不會觸發更新
    messages.value.push({ id: nextId(), role: 'assistant', content: '', status: 'streaming' })
    const reply = messages.value[messages.value.length - 1]!

    const trace = useTraceStore()
    trace.begin()
    controller = new AbortController()

    try {
      await streamChat(
        sessionId.value,
        trimmed,
        (event) => {
          switch (event.type) {
            case 'delta': // 逐字片段:追加(打字機)
              reply.content += event.text
              trace.answering()
              break
            case 'text': // 段落完整彙總:覆蓋,不能追加(否則同段話出現兩次)
              reply.content = event.text
              break
            case 'tool_call':
              trace.toolCall(event.tool, event.args)
              break
            case 'tool_result':
              trace.toolResult(event.tool, event.response)
              break
            case 'error':
              throw new Error(event.message)
            case 'done':
              break
          }
        },
        controller.signal,
      )
      reply.status = 'done'
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') {
        // 使用者主動中止:不是錯誤,保留已收到的內容
        reply.status = 'done'
        reply.content += reply.content ? '\n\n*(已中止回應)*' : '*(已中止)*'
      } else {
        console.error(err)
        reply.status = 'error'
        if (!reply.content) reply.content = '(沒有收到回應)'
      }
    } finally {
      controller = null
      trace.end()
    }
  }

  /** 中止進行中的串流(打斷 AI 說話) */
  function stopStreaming() {
    controller?.abort()
  }

  return { messages, sessionId, isStreaming, sendMessage, stopStreaming }
})

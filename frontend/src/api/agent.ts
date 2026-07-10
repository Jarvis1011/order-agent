// 與自訂後端(server/main.py)溝通:POST /chat,解析自訂 SSE 事件協定

/** 後端自訂事件協定(與 server/main.py 的 sse() 一一對應) */
export type ChatEvent =
  | { type: 'delta'; text: string } // 逐字片段 → 追加
  | { type: 'text'; text: string } // 段落完整文字 → 覆蓋
  | { type: 'tool_call'; tool: string; args: Record<string, unknown> }
  | { type: 'tool_result'; tool: string; response: unknown }
  | { type: 'done' }
  | { type: 'error'; message: string }

export async function streamChat(
  sessionId: string,
  message: string,
  onEvent: (event: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
    signal,
  })
  if (!res.ok || !res.body) {
    throw new Error(`chat 失敗:HTTP ${res.status}`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    // 網路 chunk 的切點是任意的,先進 buffer、以空行切出完整事件才解析
    buffer += decoder.decode(value, { stream: true })

    let boundary: number
    while ((boundary = buffer.indexOf('\n\n')) !== -1) {
      const rawEvent = buffer.slice(0, boundary)
      buffer = buffer.slice(boundary + 2)

      for (const line of rawEvent.split('\n')) {
        if (!line.startsWith('data:')) continue
        onEvent(JSON.parse(line.slice(5).trim()) as ChatEvent)
      }
    }
  }
}

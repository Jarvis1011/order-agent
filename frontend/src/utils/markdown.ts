import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: false, // ★ 關鍵:不放行原始 HTML,LLM 輸出的 <script> 會被轉義成純文字 → v-html 才安全
  linkify: true, // 自動把網址變成連結
  breaks: true, // 單一換行就 <br>,符合聊天情境的直覺
})

// 連結一律開新分頁 + 防 window.opener 攻擊
const defaultLinkRenderer =
  md.renderer.rules.link_open ??
  ((tokens, idx, options, _env, self) => self.renderToken(tokens, idx, options))

md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  tokens[idx]!.attrSet('target', '_blank')
  tokens[idx]!.attrSet('rel', 'noopener noreferrer')
  return defaultLinkRenderer(tokens, idx, options, env, self)
}

export function renderMarkdown(source: string): string {
  return md.render(source)
}

from google.adk.agents import Agent

from .tools import flag_delayed_orders, get_sales_summary, query_orders


def get_today() -> str:
    """取得今天的日期,格式為 YYYY-MM-DD。當問題涉及「今天」「本週」「最近」等
    時間概念時,先呼叫此工具再進行推算。"""
    from datetime import date
    return date.today().isoformat()


root_agent = Agent(
    name="order_agent",
    model="gemini-2.5-flash",
    description="訂單管理助手,能查詢訂單、統計銷售、標記延誤訂單。",
    instruction="""你是「訂單管家」,一個訂單管理助手。使用繁體中文回答。

規則:
1. 回答任何關於訂單、銷售、客戶的問題,必須先呼叫工具取得真實資料,嚴禁憑空捏造數字。
2. 涉及時間的問題(本週、上個月、最近),先用 get_today 取得今天日期再推算。
3. 會修改資料的操作(如標記延誤訂單),必須先向使用者說明將發生什麼並取得同意,才能執行。
4. 金額以千分位呈現,多筆資料用表格整理,最後給一句簡短的重點結論。
5. 如果工具回傳空結果,如實告知查無資料,不要編造。""",
    tools=[get_today, query_orders, get_sales_summary, flag_delayed_orders],
)

import sqlite3
from datetime import date
from pathlib import Path

# 用「這個檔案的位置」推算資料庫路徑,而不是相對路徑——
# 這樣不管從哪個目錄啟動程式都找得到 DB(常見坑,下面解釋)
DB_PATH = Path(__file__).resolve().parent.parent / "db" / "orders.db"


def _connect() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row  # 查詢結果可用欄位名取值,方便轉 dict
    return db


def query_orders(
    status: str = "",
    customer_name: str = "",
    order_date_from: str = "",
    order_date_to: str = "",
) -> list[dict]:
    """查詢訂單列表。可依訂單狀態、客戶名稱(模糊比對)、下單日期區間過濾,
    所有條件皆可留空、可自由組合。

    Args:
        status: 訂單狀態,可為 pending(待處理)、shipped(已出貨)、
            delayed(延誤)、done(已完成),留空表示不過濾狀態。
        customer_name: 客戶名稱關鍵字,留空表示不過濾客戶。
        order_date_from: 下單日期起(含),格式 YYYY-MM-DD,留空表示不限。
        order_date_to: 下單日期迄(含),格式 YYYY-MM-DD,留空表示不限。

    Returns:
        訂單列表(最多 50 筆),每筆含 id、客戶名、城市、狀態、金額、下單日、應出貨日。
    """
    sql = """
        SELECT o.id, c.name AS customer, c.city, o.status, o.amount,
               o.order_date, o.due_date
        FROM orders o
        JOIN customers c ON c.id = o.customer_id
        WHERE 1 = 1
    """
    params: list = []
    if status:
        sql += " AND o.status = ?"
        params.append(status)
    if customer_name:
        sql += " AND c.name LIKE ?"
        params.append(f"%{customer_name}%")
    if order_date_from:
        sql += " AND o.order_date >= ?"
        params.append(order_date_from)
    if order_date_to:
        sql += " AND o.order_date <= ?"
        params.append(order_date_to)
    sql += " ORDER BY o.due_date DESC LIMIT 50"

    db = _connect()
    rows = [dict(r) for r in db.execute(sql, params)]
    db.close()
    return rows


def get_sales_summary(group_by: str) -> list[dict]:
    """統計銷售金額。當使用者詢問營收、銷售額、業績排名等彙總性問題時使用。

    Args:
        group_by: 統計維度,必須是 "month"(按月統計)或 "customer"(按客戶統計)。

    Returns:
        統計列表,每筆含分組名稱、訂單數、總金額。
    """
    if group_by == "month":
        sql = """
            SELECT substr(order_date, 1, 7) AS name,
                   COUNT(*) AS order_count, SUM(amount) AS total_amount
            FROM orders GROUP BY name ORDER BY name
        """
    elif group_by == "customer":
        sql = """
            SELECT c.name AS name,
                   COUNT(*) AS order_count, SUM(o.amount) AS total_amount
            FROM orders o JOIN customers c ON c.id = o.customer_id
            GROUP BY c.name ORDER BY total_amount DESC
        """
    else:
        return [{"error": "group_by 必須是 'month' 或 'customer'"}]

    db = _connect()
    rows = [dict(r) for r in db.execute(sql)]
    db.close()
    return rows


def flag_delayed_orders() -> dict:
    """找出所有已超過應出貨日但仍未出貨的訂單,並將其標記為 delayed。
    這是一個「修改資料」的操作,執行前應先向使用者確認。

    Returns:
        本次標記的訂單數量與訂單 id 列表。
    """
    today = date.today().isoformat()
    db = _connect()
    rows = db.execute(
        "SELECT id FROM orders WHERE due_date < ? AND status = 'pending'",
        (today,),
    ).fetchall()
    ids = [r["id"] for r in rows]
    db.executemany(
        "UPDATE orders SET status = 'delayed' WHERE id = ?",
        [(i,) for i in ids],
    )
    db.commit()
    db.close()
    return {"flagged_count": len(ids), "order_ids": ids}


if __name__ == "__main__":
    # 手動測試區:直接執行這個檔案時才會跑,被 import 時不會
    print("延誤訂單:", query_orders(status="delayed")[:2])
    print("按月統計:", get_sales_summary("month")[:3])
    print("標記結果:", flag_delayed_orders())
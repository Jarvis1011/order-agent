import re
from datetime import date

from my_agent.tools import flag_delayed_orders, get_sales_summary, query_orders


def test_query_orders_filters_by_status():
    rows = query_orders(status="delayed")
    assert len(rows) > 0
    assert all(r["status"] == "delayed" for r in rows)


def test_query_orders_filters_by_customer():
    keyword = query_orders()[0]["customer"][:2]  # 從現有資料抓個關鍵字來測模糊查詢
    rows = query_orders(customer_name=keyword)
    assert len(rows) > 0
    assert all(keyword in r["customer"] for r in rows)


def test_query_orders_respects_limit():
    assert len(query_orders()) <= 50


def test_sales_summary_by_month():
    rows = get_sales_summary("month")
    assert len(rows) > 0
    for r in rows:
        assert re.fullmatch(r"\d{4}-\d{2}", r["name"])  # 分組名稱應是 YYYY-MM
        assert r["total_amount"] > 0


def test_sales_summary_by_customer_is_sorted():
    totals = [r["total_amount"] for r in get_sales_summary("customer")]
    assert totals == sorted(totals, reverse=True)  # 應由大到小排列


def test_sales_summary_rejects_bad_group_by():
    assert "error" in get_sales_summary("week")[0]


def test_flag_delayed_orders_clears_overdue_pending():
    result = flag_delayed_orders()
    assert result["flagged_count"] == len(result["order_ids"])
    # 執行過後,不應該再存在「已逾期但仍是 pending」的訂單
    today = date.today().isoformat()
    leftovers = [r for r in query_orders(status="pending") if r["due_date"] < today]
    assert leftovers == []

def test_query_orders_filters_by_date_range():
    rows = query_orders(order_date_from="2026-06-01", order_date_to="2026-06-30")
    assert len(rows) > 0
    assert all("2026-06-01" <= r["order_date"] <= "2026-06-30" for r in rows)
import random
import sqlite3
from datetime import date, timedelta

from faker import Faker

fake = Faker("zh_TW")   # 生成繁中假資料(公司名、城市)
random.seed(42)          # 固定隨機種子:每次執行結果都一樣,方便之後寫測試

db = sqlite3.connect("db/orders.db")

# 先清空,讓這個腳本可以重複執行(注意順序:先刪子表再刪父表,不然外鍵會擋)
db.executescript("""
    DELETE FROM order_items;
    DELETE FROM orders;
    DELETE FROM products;
    DELETE FROM customers;
""")

# 1. 客戶 20 家
customers = []
for _ in range(20):
    cur = db.execute(
        "INSERT INTO customers (name, city) VALUES (?, ?)",
        (fake.company(), fake.city_name()),
    )
    customers.append(cur.lastrowid)

# 2. 商品 15 種
products = {}
for i in range(15):
    price = random.randint(100, 5000)
    cur = db.execute(
        "INSERT INTO products (name, price) VALUES (?, ?)",
        (f"零件-{i + 1:02d}", price),
    )
    products[cur.lastrowid] = price

# 3. 訂單 300 筆,散布在過去半年
today = date.today()
for _ in range(300):
    order_date = today - timedelta(days=random.randint(0, 180))
    due_date = order_date + timedelta(days=random.randint(7, 30))

    if due_date < today:
        # 已過應出貨日:大多完成,故意留一批延誤的(demo 的戲肉)
        status = random.choices(["done", "shipped", "delayed"], weights=[70, 15, 15])[0]
    else:
        status = random.choices(["pending", "shipped"], weights=[60, 40])[0]

    cur = db.execute(
        "INSERT INTO orders (customer_id, status, amount, order_date, due_date) "
        "VALUES (?, ?, 0, ?, ?)",
        (random.choice(customers), status, order_date.isoformat(), due_date.isoformat()),
    )
    order_id = cur.lastrowid

    # 每張訂單 1~4 個品項,訂單金額 = 品項小計加總
    amount = 0
    for product_id in random.sample(list(products), random.randint(1, 4)):
        qty = random.randint(1, 20)
        db.execute(
            "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
            (order_id, product_id, qty),
        )
        amount += products[product_id] * qty
    db.execute("UPDATE orders SET amount = ? WHERE id = ?", (amount, order_id))

db.commit()  # 寫入磁碟,沒 commit 資料不會真的存進去

for status, cnt in db.execute("SELECT status, COUNT(*) FROM orders GROUP BY status"):
    print(f"{status}: {cnt} 筆")
db.close()
print("Seed 完成")
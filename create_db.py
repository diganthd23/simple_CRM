import sqlite3

conn = sqlite3.connect("crm.db")
cur = conn.cursor()

# PRODUCTS
cur.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    price TEXT
)
""")

# LEADS
cur.execute("""
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    email TEXT,
    product TEXT,
    budget TEXT,
    status TEXT DEFAULT 'Open',
    score INTEGER DEFAULT 5,
    priority TEXT DEFAULT 'Low'
)
""")

# DEALS
cur.execute("""
CREATE TABLE IF NOT EXISTS deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_name TEXT,
    product TEXT,
    amount TEXT,
    status TEXT
)
""")

# REMINDERS
cur.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    date TEXT,
    response TEXT DEFAULT 'Pending'
)
""")

conn.commit()
conn.close()

print("✅ crm.db recreated successfully")

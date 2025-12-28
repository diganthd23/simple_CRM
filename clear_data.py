import sqlite3

conn = sqlite3.connect("crm.db")
cur = conn.cursor()

cur.execute("DELETE FROM reminders")
cur.execute("DELETE FROM deals")
cur.execute("DELETE FROM leads")
cur.execute("DELETE FROM products")

conn.commit()
conn.close()

print("All CRM data cleared successfully")

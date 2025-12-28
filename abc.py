import sqlite3
import os

DB = "crm.db"

def get_db():
    return sqlite3.connect(DB)

def setup_db():
    db = get_db()
    cur = db.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        price REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        product TEXT,
        budget REAL,
        score INTEGER DEFAULT 0,
        priority TEXT DEFAULT 'Low',
        status TEXT DEFAULT 'Open'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS deals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_name TEXT,
        product TEXT,
        amount REAL,
        status TEXT
    )
    """)

    db.commit()
    db.close()

def priority_from_score(score):
    if score >= 40:
        return "High"
    elif score >= 20:
        return "Medium"
    return "Low"

# ---------- MENU FUNCTIONS ----------

def add_product():
    name = input("Product name: ")
    category = input("Category: ")
    price = float(input("Price: "))

    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO products (name,category,price) VALUES (?,?,?)",
                (name, category, price))
    db.commit()
    db.close()
    print("✔ Product added")

def add_lead():
    name = input("Lead name: ")
    phone = input("Phone: ")
    email = input("Email: ")
    product = input("Interested product: ")
    budget = float(input("Budget: "))

    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO leads (name,phone,email,product,budget)
        VALUES (?,?,?,?,?)
    """, (name, phone, email, product, budget))
    db.commit()
    db.close()
    print("✔ Lead added")

def view_leads():
    db = get_db()
    cur = db.cursor()
    leads = cur.execute("SELECT id,name,product,budget,score,priority,status FROM leads").fetchall()
    db.close()

    print("\n--- LEADS ---")
    for l in leads:
        print(l)

def close_lead():
    lead_id = int(input("Enter Lead ID to close: "))

    db = get_db()
    cur = db.cursor()

    lead = cur.execute(
        "SELECT name,product,budget,score FROM leads WHERE id=?",
        (lead_id,)
    ).fetchone()

    if not lead:
        print("❌ Lead not found")
        return

    new_score = lead[3] + 20
    cur.execute("INSERT INTO deals (lead_name,product,amount,status) VALUES (?,?,?,?)",
                (lead[0], lead[1], lead[2], "Closed"))

    cur.execute("""
        UPDATE leads
        SET status='Closed', score=?, priority=?
        WHERE id=?
    """, (new_score, priority_from_score(new_score), lead_id))

    db.commit()
    db.close()
    print("✔ Lead closed & deal created")

def view_deals():
    db = get_db()
    cur = db.cursor()
    deals = cur.execute("SELECT * FROM deals").fetchall()
    db.close()

    print("\n--- DEALS ---")
    for d in deals:
        print(d)

def reset_all():
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM products")
    cur.execute("DELETE FROM leads")
    cur.execute("DELETE FROM deals")
    db.commit()
    db.close()
    print("✔ All data cleared")

# ---------- MAIN LOOP ----------

def main():
    setup_db()

    while True:
        print("""
====== SIMPLE CRM (CONSOLE) ======
1. Add Product
2. Add Lead
3. View Leads
4. Close Lead
5. View Deals
6. Reset All Data
0. Exit
""")
        choice = input("Enter choice: ")

        if choice == "1":
            add_product()
        elif choice == "2":
            add_lead()
        elif choice == "3":
            view_leads()
        elif choice == "4":
            close_lead()
        elif choice == "5":
            view_deals()
        elif choice == "6":
            reset_all()
        elif choice == "0":
            print("Exiting CRM...")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()

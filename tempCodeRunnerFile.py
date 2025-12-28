from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "croma_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "crm.db")

def get_db():
    return sqlite3.connect(DB_PATH)

# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "employee" and request.form["password"] == "croma":
            session["user"] = "employee"
            return redirect("/dashboard")
    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")

# ---------- LEADS ----------
@app.route("/leads", methods=["GET", "POST"])
def leads():
    if "user" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        cur.execute("""
            INSERT INTO leads (name, phone, email, product, budget, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            request.form["name"],
            request.form["phone"],
            request.form["email"],
            request.form["product"],
            request.form["budget"],
            "Open"
        ))
        db.commit()

    leads_data = cur.execute("SELECT * FROM leads").fetchall()
    products = cur.execute("SELECT name FROM products").fetchall()

    return render_template("leads.html", leads=leads_data, products=products)

# ---------- CLOSE LEAD ----------
@app.route("/close_lead/<int:id>")
def close_lead(id):
    if "user" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    lead = cur.execute(
        "SELECT name, product, budget FROM leads WHERE id=?",
        (id,)
    ).fetchone()

    if lead:
        cur.execute("""
            INSERT INTO deals (lead_name, product, amount, status)
            VALUES (?, ?, ?, ?)
        """, (lead[0], lead[1], lead[2], "Closed"))

        cur.execute("UPDATE leads SET status='Closed' WHERE id=?", (id,))
        db.commit()

    return redirect("/deals")

# ---------- DELETE LEAD ----------
@app.route("/delete_lead/<int:id>")
def delete_lead(id):
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM leads WHERE id=?", (id,))
    db.commit()
    return redirect("/leads")

# ---------- PRODUCTS ----------
@app.route("/products", methods=["GET", "POST"])
def products():
    if "user" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        cur.execute("""
            INSERT INTO products (name, category, price)
            VALUES (?, ?, ?)
        """, (
            request.form["name"],
            request.form["category"],
            request.form["price"]
        ))
        db.commit()

    products_data = cur.execute("SELECT * FROM products").fetchall()
    return render_template("products.html", products=products_data)

# ---------- DEALS ----------
@app.route("/deals")
def deals():
    if "user" not in session:
        return redirect("/")
    db = get_db()
    cur = db.cursor()
    deals_data = cur.execute("SELECT * FROM deals").fetchall()
    return render_template("deals.html", deals=deals_data)

# ---------- REMINDERS ----------
@app.route("/reminders", methods=["GET", "POST"])
def reminders():
    if "user" not in session:
        return redirect("/")

    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        cur.execute("""
            INSERT INTO reminders (lead_id, date, note)
            VALUES (?, ?, ?)
        """, (
            request.form["lead_id"],
            request.form["date"],
            request.form["note"]
        ))
        db.commit()

    leads = cur.execute("SELECT id, name FROM leads").fetchall()

    reminders_data = cur.execute("""
        SELECT reminders.id, leads.name, reminders.date, reminders.note
        FROM reminders
        JOIN leads ON reminders.lead_id = leads.id
    """).fetchall()

    return render_template("reminders.html", reminders=reminders_data, leads=leads)

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)

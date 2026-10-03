from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


# ==========================================
# CREATE DATABASE TABLES
# ==========================================

def init_db():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL,
            venue TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            email TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(id)
        )
    """)

    conn.commit()

    conn.close()


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM events
        ORDER BY date
        LIMIT 3
    """)

    events = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        events=events
    )


# ==========================================
# EXPLORE EVENTS
# ==========================================

@app.route("/events")
def events():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM events
        ORDER BY date
    """)

    events = cursor.fetchall()

    conn.close()

    return render_template(
        "events.html",
        events=events
    )


# ==========================================
# EVENT DETAILS
# ==========================================

@app.route("/event/<int:event_id>")
def event_details(event_id):

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM events
        WHERE id = ?
    """, (event_id,))

    event = cursor.fetchone()

    conn.close()

    if event is None:

        return "Event not found", 404

    return render_template(
        "event_details.html",
        event=event
    )


# ==========================================
# CREATE EVENT
# ==========================================

@app.route("/add-event", methods=["GET", "POST"])
def add_event():

    if request.method == "POST":

        name = request.form.get("name")
        description = request.form.get("description")
        date = request.form.get("date")
        venue = request.form.get("venue")

        if not name or not description or not date or not venue:

            return "Please fill all fields", 400

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO events
            (name, description, date, venue)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            description,
            date,
            venue
        ))

        conn.commit()

        conn.close()

        return redirect(url_for("events"))

    return render_template("add_event.html")


# ==========================================
# REGISTER FOR EVENT
# ==========================================

@app.route("/register/<int:event_id>", methods=["POST"])
def register(event_id):

    student_name = request.form.get("student_name")
    email = request.form.get("email")

    if not student_name or not email:

        return "Please enter your name and email", 400

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM events
        WHERE id = ?
    """, (event_id,))

    event = cursor.fetchone()

    if event is None:

        conn.close()

        return "Event not found", 404

    cursor.execute("""
        INSERT INTO registrations
        (student_name, email, event_id)
        VALUES (?, ?, ?)
    """, (
        student_name,
        email,
        event_id
    ))

    conn.commit()

    conn.close()

    return redirect(url_for("registrations"))


# ==========================================
# MY REGISTRATIONS
# ==========================================

@app.route("/registrations")
def registrations():

    conn = get_db_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            registrations.id,
            registrations.student_name,
            registrations.email,
            events.name AS event_name,
            events.date AS event_date,
            events.venue AS event_venue
        FROM registrations
        JOIN events
        ON registrations.event_id = events.id
        ORDER BY events.date
    """)

    registrations = cursor.fetchall()

    conn.close()

    return render_template(
        "registrations.html",
        registrations=registrations
    )


# ==========================================
# RUN APPLICATION
# ==========================================
if __name__ == "__main__":
    init_db()
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
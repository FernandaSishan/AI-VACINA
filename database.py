import sqlite3
from pathlib import Path
from datetime import date, timedelta

DB_PATH = Path(__file__).with_name("vacia.db")

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, birth_date TEXT NOT NULL, phone TEXT, responsible TEXT
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS vaccinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL, vaccine TEXT NOT NULL, dose TEXT NOT NULL,
            applied_date TEXT NOT NULL, next_due_date TEXT, health_unit TEXT,
            FOREIGN KEY(person_id) REFERENCES people(id) ON DELETE CASCADE
        )""")

def add_person(name, birth_date, phone="", responsible=""):
    with connect() as conn:
        conn.execute("INSERT INTO people(name,birth_date,phone,responsible) VALUES(?,?,?,?)",
                     (name,birth_date,phone,responsible))

def list_people():
    with connect() as conn:
        return conn.execute("SELECT id,name,birth_date,phone,responsible FROM people ORDER BY name").fetchall()

def add_vaccination(person_id, vaccine, dose, applied_date, next_due_date, health_unit=""):
    with connect() as conn:
        conn.execute("""INSERT INTO vaccinations(person_id,vaccine,dose,applied_date,next_due_date,health_unit)
                        VALUES(?,?,?,?,?,?)""",
                     (person_id,vaccine,dose,applied_date,next_due_date,health_unit))

def list_vaccinations():
    with connect() as conn:
        return conn.execute("""SELECT v.id,p.name,v.vaccine,v.dose,v.applied_date,v.next_due_date,v.health_unit
                               FROM vaccinations v JOIN people p ON p.id=v.person_id
                               ORDER BY COALESCE(v.next_due_date,'9999-12-31'),p.name""").fetchall()

def classify_for_dashboard(next_due, today):
    if not next_due: return "Sem data"
    due = date.fromisoformat(next_due)
    if due < today: return "Atrasada"
    if due <= today + timedelta(days=7): return "Próxima"
    return "Em dia"

def dashboard_data():
    people_count = len(list_people())
    records = list_vaccinations()
    today = date.today()
    upcoming = sum(1 for r in records if classify_for_dashboard(r[5],today)=="Próxima")
    overdue = sum(1 for r in records if classify_for_dashboard(r[5],today)=="Atrasada")
    recent = sorted(records, key=lambda r: r[4], reverse=True)[:8]
    recent_rows = [(r[1],r[2],r[3],r[4],r[5] or "Não informada") for r in recent]
    return people_count,len(records),upcoming,overdue,recent_rows

def delete_person(person_id):
    with connect() as conn:
        conn.execute("DELETE FROM people WHERE id=?",(person_id,))

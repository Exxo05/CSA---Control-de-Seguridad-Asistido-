# servicios/db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "datos" / "base.db"

def crear_bd_si_no_existe():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS incidentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        tipo TEXT NOT NULL,
        descripcion TEXT,
        lat REAL,
        lon REAL,
        gravedad TEXT
    );
    """)
    conn.commit()
    conn.close()

def get_conn():
    crear_bd_si_no_existe()
    return sqlite3.connect(DB_PATH)

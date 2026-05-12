# servicios/db.py — Base de datos v2.0 con inicialización completa
import sqlite3, os, hashlib, shutil
from datetime import datetime

def get_connection():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path  = os.path.join(base_dir, "datos", "base.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")   # mejor concurrencia
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def inicializar_bd():
    """Crea todas las tablas si no existen. Idempotente."""
    conn = get_connection()
    c    = conn.cursor()

    # ── Usuarios / sesiones ───────────────────────────────────────
    c.executescript("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario     TEXT UNIQUE NOT NULL,
        hash_pwd    TEXT NOT NULL,
        nombre      TEXT NOT NULL,
        rol         TEXT NOT NULL DEFAULT 'operador',
        activo      INTEGER NOT NULL DEFAULT 1,
        created_at  TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS sesiones (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
        inicio      TEXT NOT NULL,
        fin         TEXT,
        turno       TEXT
    );

    -- ── Incidentes ─────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS incidentes (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo        TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        fecha       TEXT NOT NULL,
        zona        TEXT NOT NULL,
        direccion   TEXT,
        estado      TEXT NOT NULL DEFAULT 'Activo',
        lat         REAL,
        lon         REAL,
        operador_id INTEGER REFERENCES usuarios(id),
        turno       TEXT
    );

    -- ── Notas internas de incidente ────────────────────────────
    CREATE TABLE IF NOT EXISTS notas_incidente (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        incidente_id INTEGER NOT NULL REFERENCES incidentes(id) ON DELETE CASCADE,
        operador_id  INTEGER REFERENCES usuarios(id),
        texto        TEXT NOT NULL,
        fecha        TEXT NOT NULL
    );

    -- ── Log de auditoría ───────────────────────────────────────
    CREATE TABLE IF NOT EXISTS auditoria (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha        TEXT NOT NULL,
        usuario_id   INTEGER REFERENCES usuarios(id),
        accion       TEXT NOT NULL,
        tabla        TEXT,
        registro_id  INTEGER,
        detalle      TEXT
    );

    -- ── Unidades ───────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS unidades (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        indicativo      TEXT UNIQUE NOT NULL,
        estado          TEXT NOT NULL DEFAULT 'Disponible',
        en_servicio     INTEGER NOT NULL DEFAULT 0,
        ubicacion_actual TEXT,
        lat             REAL,
        lon             REAL,
        ultima_pos      TEXT
    );

    -- ── Personas ───────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS personas (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre       TEXT NOT NULL,
        apellidos    TEXT,
        dni          TEXT,
        fecha_nac    TEXT,
        nacionalidad TEXT DEFAULT 'Española',
        telefono     TEXT,
        domicilio    TEXT,
        notas        TEXT,
        created_at   TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS personas_incidentes (
        persona_id   INTEGER NOT NULL REFERENCES personas(id) ON DELETE CASCADE,
        incidente_id INTEGER NOT NULL REFERENCES incidentes(id) ON DELETE CASCADE,
        rol          TEXT NOT NULL DEFAULT 'implicado',
        PRIMARY KEY (persona_id, incidente_id)
    );

    -- ── Vehículos ──────────────────────────────────────────────
    CREATE TABLE IF NOT EXISTS vehiculos (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        matricula    TEXT UNIQUE NOT NULL,
        marca        TEXT,
        modelo       TEXT,
        color        TEXT,
        tipo         TEXT DEFAULT 'Turismo',
        propietario  TEXT,
        notas        TEXT,
        alerta       INTEGER DEFAULT 0,
        motivo_alerta TEXT,
        created_at   TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS vehiculos_incidentes (
        vehiculo_id  INTEGER NOT NULL REFERENCES vehiculos(id) ON DELETE CASCADE,
        incidente_id INTEGER NOT NULL REFERENCES incidentes(id) ON DELETE CASCADE,
        PRIMARY KEY (vehiculo_id, incidente_id)
    );

    -- ── Histórico de delitos ───────────────────────────────────
    CREATE TABLE IF NOT EXISTS delitos_historicos (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo        TEXT,
        fecha       TEXT,
        lat         REAL,
        lon         REAL,
        zona        TEXT,
        descripcion TEXT
    );
    """)

    # Migración silenciosa: añadir columnas nuevas si no existen
    _migrar(c, "incidentes",  "lat",         "REAL")
    _migrar(c, "incidentes",  "lon",         "REAL")
    _migrar(c, "incidentes",  "operador_id", "INTEGER")
    _migrar(c, "incidentes",  "turno",       "TEXT")
    _migrar(c, "unidades",    "lat",         "REAL")
    _migrar(c, "unidades",    "lon",         "REAL")
    _migrar(c, "unidades",    "ultima_pos",  "TEXT")

    # Usuario admin por defecto
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO usuarios (usuario,hash_pwd,nombre,rol,activo,created_at)"
            " VALUES (?,?,?,?,?,?)",
            ("admin", _hash("admin123"), "Administrador", "admin", 1,
             datetime.now().isoformat())
        )
        c.execute(
            "INSERT INTO usuarios (usuario,hash_pwd,nombre,rol,activo,created_at)"
            " VALUES (?,?,?,?,?,?)",
            ("operador", _hash("csa2025"), "Operador Sala", "operador", 1,
             datetime.now().isoformat())
        )

    # Patrullas por defecto
    c.execute("SELECT COUNT(*) FROM unidades")
    if c.fetchone()[0] == 0:
        patrullas = [
            ("Z-10", "Disponible", 0, "Casco Histórico / Centro"),
            ("Z-20", "Disponible", 0, "Reyes Católicos"),
            ("Z-30", "Disponible", 0, "Chorrillo / Ensanche"),
            ("Z-40", "Disponible", 0, "La Garena"),
            ("K-5",  "Disponible", 0, "Espartales"),
            ("A-1",  "Disponible", 0, "El Val"),
        ]
        c.executemany(
            "INSERT INTO unidades (indicativo, estado, en_servicio, ubicacion_actual)"
            " VALUES (?,?,?,?)",
            patrullas
        )

    conn.commit()
    conn.close()


def _migrar(cursor, tabla, columna, tipo):
    try:
        cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")
    except Exception:
        pass


def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()


def verificar_usuario(usuario: str, pwd: str):
    """Devuelve dict con datos del usuario o None."""
    conn = get_connection()
    c    = conn.cursor()
    c.execute("SELECT id,usuario,nombre,rol,activo FROM usuarios WHERE usuario=? AND hash_pwd=?",
              (usuario, _hash(pwd)))
    row = c.fetchone()
    conn.close()
    if row and row[4]:
        return {"id": row[0], "usuario": row[1], "nombre": row[2], "rol": row[3]}
    return None


def registrar_auditoria(usuario_id, accion, tabla=None, registro_id=None, detalle=None):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO auditoria (fecha,usuario_id,accion,tabla,registro_id,detalle)"
            " VALUES (?,?,?,?,?,?)",
            (datetime.now().isoformat(), usuario_id, accion, tabla, registro_id, detalle)
        )
        conn.commit()
    finally:
        conn.close()


def hacer_backup():
    """Copia la BD a datos/backups/base_YYYYMMDD_HHMMSS.db"""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src  = os.path.join(base, "datos", "base.db")
    dst_dir = os.path.join(base, "datos", "backups")
    os.makedirs(dst_dir, exist_ok=True)
    nombre = f"base_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    dst    = os.path.join(dst_dir, nombre)
    try:
        shutil.copy2(src, dst)
        # Borrar backups con más de 30 días
        _limpiar_backups_viejos(dst_dir, dias=30)
        return dst
    except Exception as e:
        return None


def _limpiar_backups_viejos(directorio: str, dias: int):
    import time
    ahora = time.time()
    for f in os.listdir(directorio):
        ruta = os.path.join(directorio, f)
        if os.path.isfile(ruta):
            edad = ahora - os.path.getmtime(ruta)
            if edad > dias * 86400:
                try:
                    os.remove(ruta)
                except Exception:
                    pass

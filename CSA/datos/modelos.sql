-- Tabla de incidentes
CREATE TABLE IF NOT EXISTS incidentes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    tipo TEXT NOT NULL,
    descripcion TEXT,
    lat REAL,
    lon REAL,
    gravedad TEXT  -- ejemplo: baja/media/alta
);

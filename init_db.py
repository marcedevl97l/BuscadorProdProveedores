import os
import sqlite3
from config import DB
from werkzeug.security import generate_password_hash

conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    codigo TEXT,
    proveedor TEXT,
    precio REAL,
    precio_escala REAL,
    fuente TEXT,
    url TEXT,
    escala TEXT,
    texto_busqueda TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password_hash TEXT
)
""")

# Insertar usuario admin por defecto si no existe
default_username = os.getenv("DEFAULT_ADMIN_USER", "SUPERVISOR")
default_password = os.getenv("DEFAULT_ADMIN_PASS", "171508")
password_hash = generate_password_hash(default_password)
c.execute(
    "INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)",
    (default_username, password_hash)
)

# Indices para mejorar busquedas
c.execute("CREATE INDEX IF NOT EXISTS idx_productos_texto ON productos(texto_busqueda)")
c.execute("CREATE INDEX IF NOT EXISTS idx_productos_proveedor ON productos(proveedor)")
c.execute("CREATE INDEX IF NOT EXISTS idx_productos_codigo ON productos(codigo)")

conn.commit()
conn.close()

print("Base de datos creada correctamente")

if os.getenv("DEFAULT_ADMIN_USER") is None or os.getenv("DEFAULT_ADMIN_PASS") is None:
    print("Aviso: usando credenciales por defecto. Configura DEFAULT_ADMIN_USER y DEFAULT_ADMIN_PASS en .env")

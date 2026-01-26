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
    fuente TEXT,
    url TEXT,
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
password_hash = generate_password_hash('171508')
c.execute("INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)", ('SUPERVISOR', password_hash))

conn.commit()
conn.close()

print("Base de datos creada correctamente")

import sqlite3
from config import DB

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

conn.commit()
conn.close()

print("Base de datos creada correctamente")

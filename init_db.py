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
    texto_busqueda TEXT,
    fecha_venc TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password_hash TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS configuraciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    clave TEXT UNIQUE,
    valor TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS personal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,         -- Nombres
    dni TEXT,                     -- DNI
    rol TEXT DEFAULT 'Trabajadora',-- Rol / Categoría
    tienda TEXT,                  -- Local / Tienda
    planilla TEXT,                -- Planilla
    af TEXT,                      -- Af
    activo INTEGER DEFAULT 1
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS ventas_mensuales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personal_id INTEGER,
    mes INTEGER,       -- 1-12
    anio INTEGER,      -- 2024, 2025...
    monto REAL DEFAULT 0,
    FOREIGN KEY(personal_id) REFERENCES personal(id)
)
""")

# Insertar configuraciones por defecto
configuraciones_iniciales = [
    ('farmacom_user', os.getenv("FARMACOM_USER", "")),
    ('farmacom_pass', os.getenv("FARMACOM_PASS", "")),
    ('farmacom_url_login', "https://farmacom.com.pe/pedidos/login.php"),
    ('farmacom_url_lista', "https://farmacom.com.pe/pedidos/lista.php"),
    ('farmacom_headless', os.getenv("FARMACOM_HEADLESS", "false")),
    ('pionero_excel_pattern', "PIONERO"),
    ('prosalud_excel_pattern', "PROSALUD")
]

for clave, valor in configuraciones_iniciales:
    c.execute("INSERT OR IGNORE INTO configuraciones (clave, valor) VALUES (?, ?)", (clave, valor))

# Insertar personal por defecto si la tabla está vacía
c.execute("SELECT COUNT(*) FROM personal")
if c.fetchone()[0] == 0:
    empleados_iniciales = [
        ('ADMINISTRADOR PRINCIPAL', 'Administrador', 'Oficina'),
        ('QUIMICO FARMACEUTICO T1', 'QF', 'Tienda 1'),
        ('QUIMICO FARMACEUTICO T2', 'QF', 'Tienda 2'),
        ('TRABAJADORA 1', 'Trabajadora', 'Tienda 1'),
        ('TRABAJADORA 2', 'Trabajadora', 'Tienda 1'),
        ('TRABAJADORA 3', 'Trabajadora', 'Tienda 1'),
        ('TRABAJADORA 4', 'Trabajadora', 'Tienda 1'),
        ('TRABAJADORA 5', 'Trabajadora', 'Tienda 2'),
        ('TRABAJADORA 6', 'Trabajadora', 'Tienda 2'),
        ('TRABAJADORA 7', 'Trabajadora', 'Tienda 2'),
        ('TRABAJADORA 8', 'Trabajadora', 'Tienda 2'),
    ]
    for nombre, rol, tienda in empleados_iniciales:
        c.execute("INSERT INTO personal (nombre, rol, tienda) VALUES (?, ?, ?)", (nombre, rol, tienda))

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

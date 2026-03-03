import sqlite3
from config import DB

conn = sqlite3.connect(DB)
c = conn.cursor()

# 1. Agregar columna ocupacion
try:
    c.execute("ALTER TABLE personal ADD COLUMN ocupacion TEXT DEFAULT 'vendedor'")
    print("Columna 'ocupacion' agregada.")
except sqlite3.OperationalError:
    print("La columna 'ocupacion' ya existe.")

# 2. Limpiar datos de prueba
# Eliminamos registros que tengan nombres genéricos de prueba o que no tengan DNI (asumiendo que los reales se registran con DNI ahora)
# También podemos simplemente vaciar la tabla si el usuario quiere empezar de cero, 
# pero el usuario dijo "solo mostrar los que sean guardados, mas no los de prueba".
# Los de prueba en init_db.py son: 'ADMINISTRADOR PRINCIPAL', 'QUIMICO FARMACEUTICO T1', 'TRABAJADORA 1', etc.

nombres_prueba = [
    'ADMINISTRADOR PRINCIPAL', 'QUIMICO FARMACEUTICO T1', 'QUIMICO FARMACEUTICO T2',
    'TRABAJADORA 1', 'TRABAJADORA 2', 'TRABAJADORA 3', 'TRABAJADORA 4',
    'TRABAJADORA 5', 'TRABAJADORA 6', 'TRABAJADORA 7', 'TRABAJADORA 8'
]

for nombre in nombres_prueba:
    c.execute("DELETE FROM personal WHERE nombre = ?", (nombre,))

print(f"Se han eliminado los {len(nombres_prueba)} registros de prueba.")

conn.commit()
conn.close()
print("Migración y limpieza completada.")

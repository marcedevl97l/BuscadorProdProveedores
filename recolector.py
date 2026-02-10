import pandas as pd
import sqlite3
import os
from normalizador import limpiar
from config import DB

def ensure_schema():
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
    c.execute("PRAGMA table_info(productos)")
    columns = [row[1] for row in c.fetchall()]
    if "url" not in columns:
        c.execute("ALTER TABLE productos ADD COLUMN url TEXT")
    if "escala" not in columns:
        c.execute("ALTER TABLE productos ADD COLUMN escala TEXT")
    if "precio_escala" not in columns:
        c.execute("ALTER TABLE productos ADD COLUMN precio_escala REAL")
    conn.commit()
    conn.close()

def limpiar_datos_excel(nombre_archivo):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM productos WHERE fuente LIKE ?", (f"{nombre_archivo}%",))
    conn.commit()
    conn.close()

def guardar_producto(data):
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    texto_busqueda = f"{data['nombre']} {data['codigo']} {data['proveedor']}"

    c.execute("""
        INSERT INTO productos
        (nombre, codigo, proveedor, precio, precio_escala, fuente, url, escala, texto_busqueda)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["nombre"],
        data["codigo"],
        data["proveedor"],
        data["precio"],
        data.get("precio_escala"),
        data["fuente"],
        data["url"],
        data.get("escala"),
        limpiar(texto_busqueda)
    ))

    conn.commit()
    conn.close()

def parse_str(value):
    if pd.isna(value):
        return ""
    return str(value)

def parse_float(value):
    if pd.isna(value):
        return None
    try:
        return float(value)
    except Exception:
        return None

def leer_excel(ruta):
    ensure_schema()
    nombre_archivo = os.path.basename(ruta)
    is_pionero = "PIONERO" in nombre_archivo.upper()

    # Limpia solo los datos que vienen de este archivo
    limpiar_datos_excel(nombre_archivo)

    hojas = pd.read_excel(ruta, sheet_name=None)
    errores = []
    guardados = 0

    for nombre_hoja, df in hojas.items():
        for idx, fila in df.iterrows():
            try:
                precio = parse_float(fila.iloc[3])
                if precio is None:
                    precio = 0.0

                escala = parse_str(fila.iloc[5]) if is_pionero else ""
                precio_escala = parse_float(fila.iloc[6]) if is_pionero else None

                producto = {
                    "codigo": parse_str(fila.iloc[0]),
                    "nombre": parse_str(fila.iloc[1]),
                    "proveedor": parse_str(fila.iloc[2]),
                    "precio": precio,
                    "precio_escala": precio_escala,
                    "fuente": f"{nombre_archivo} | Hoja: {nombre_hoja} | Fila: {idx + 2}",
                    "url": "",
                    "escala": escala
                }
                guardar_producto(producto)
                guardados += 1
            except Exception as exc:
                errores.append((nombre_hoja, idx + 2, str(exc)))

    print(f"{nombre_archivo}: {guardados} productos guardados")
    if errores:
        print(f"{nombre_archivo}: {len(errores)} filas con error")

if __name__ == "__main__":
    leer_excel("data/PIONERO FEB26.xlsx")
    leer_excel("data/PROSALUD EN26.xlsx")
    print("Datos de Excel actualizados sin borrar Farmacom")

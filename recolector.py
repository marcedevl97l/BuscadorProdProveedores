import pandas as pd
import sqlite3
import os
from normalizador import limpiar
from config import DB

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
        (nombre, codigo, proveedor, precio, fuente, url, texto_busqueda)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["nombre"],
        data["codigo"],
        data["proveedor"],
        data["precio"],
        data["fuente"],
        data["url"],
        limpiar(texto_busqueda)
    ))

    conn.commit()
    conn.close()

def leer_excel(ruta):
    nombre_archivo = os.path.basename(ruta)

    # Limpia solo los datos que vienen de este archivo
    limpiar_datos_excel(nombre_archivo)

    hojas = pd.read_excel(ruta, sheet_name=None)

    for nombre_hoja, df in hojas.items():
        for idx, fila in df.iterrows():
            try:
                producto = {
                    "codigo": str(fila.iloc[0]),
                    "nombre": str(fila.iloc[1]),
                    "proveedor": str(fila.iloc[2]),
                    "precio": float(fila.iloc[3]),
                    "fuente": f"{nombre_archivo} | Hoja: {nombre_hoja} | Fila: {idx + 2}",
                    "url": ""
                }
                guardar_producto(producto)
            except Exception:
                pass

if __name__ == "__main__":
    leer_excel("data/PIONERO FEB26.xlsx")
    leer_excel("data/PROSALUD EN26.xlsx")
    print("Datos de Excel actualizados sin borrar Farmacom")

from flask import Flask, render_template, request
import sqlite3
from config import DB
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    resultados = []
    sin_stock = False
    proveedores = []
    fuentes = []
    fecha_actualizacion = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Obtener proveedores y fuentes únicos
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT DISTINCT proveedor FROM productos WHERE proveedor != '' ORDER BY proveedor")
    proveedores = [row[0] for row in c.fetchall()]
    c.execute("SELECT DISTINCT fuente FROM productos ORDER BY fuente")
    fuentes_raw = [row[0] for row in c.fetchall()]
    # Procesar fuentes para mostrar solo el nombre principal
    fuentes = list(set([f.split(' | ')[0] for f in fuentes_raw]))
    conn.close()

    if request.method == "POST":
        q = request.form["q"].lower()
        proveedor_filtro = request.form.get("proveedor", "todos")

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        query = """
            SELECT nombre, codigo, proveedor, precio, fuente
            FROM productos
            WHERE texto_busqueda LIKE ?
        """
        params = [f"%{q}%"]

        if proveedor_filtro != "todos":
            query += " AND proveedor = ?"
            params.append(proveedor_filtro)

        query += " LIMIT 50"

        c.execute(query, params)
        resultados = c.fetchall()
        conn.close()

        if len(resultados) == 0:
            sin_stock = True

    return render_template(
        "index.html",
        resultados=resultados,
        sin_stock=sin_stock,
        proveedores=proveedores,
        fuentes=fuentes,
        fecha_actualizacion=fecha_actualizacion
    )

if __name__ == "__main__":
    app.run(debug=True)

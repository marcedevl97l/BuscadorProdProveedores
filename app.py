import math
import os
from flask import Flask, render_template, request, session, redirect, url_for, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from config import DB
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from io import BytesIO
from normalizador import limpiar

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'super_secret_key_change_this_in_production')


# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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

ensure_schema()

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, username, password_hash FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1], user[2])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
        user_data = c.fetchone()
        conn.close()
        
        if user_data and check_password_hash(user_data[2], password):
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Usuario o contraseña incorrecta. Por favor, vuelve a intentar.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/ping')
def ping():
    return '', 204

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    resultados = []
    sin_stock = False
    proveedores = []
    fuentes = []
    fecha_actualizacion = datetime.now().strftime("%d/%m/%Y %H:%M")
    current_q = ""
    current_proveedor = "todos"
    current_sort = "nombre_asc"
    page = 1
    per_page = 50
    total_count = 0
    total_pages = 0

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
        q_raw = request.form.get("q", "")
        current_q = q_raw
        q = limpiar(q_raw)
        current_proveedor = request.form.get("proveedor", "todos")
        current_sort = request.form.get("sort", "nombre_asc")
        page = max(1, int(request.form.get("page", 1)))

        where_clauses = []
        params = []

        if q:
            where_clauses.append("texto_busqueda LIKE ?")
            params.append(f"%{q}%")

        if current_proveedor != "todos":
            where_clauses.append("proveedor = ?")
            params.append(current_proveedor)

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        sort_map = {
            "nombre_asc": "nombre ASC",
            "nombre_desc": "nombre DESC"
        }
        order_by = sort_map.get(current_sort, "nombre ASC")

        conn = sqlite3.connect(DB)
        c = conn.cursor()

        count_query = f"SELECT COUNT(*) FROM productos WHERE {where_sql}"
        c.execute(count_query, params)
        total_count = c.fetchone()[0]
        total_pages = max(1, math.ceil(total_count / per_page)) if total_count > 0 else 0

        if total_pages > 0 and page > total_pages:
            page = total_pages

        query = f"""
            SELECT nombre, codigo, proveedor, precio, fuente, escala, precio_escala
            FROM productos
            WHERE {where_sql}
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
        """
        params_query = params + [per_page, (page - 1) * per_page]

        c.execute(query, params_query)
        resultados = c.fetchall()
        conn.close()

        if total_count == 0:
            sin_stock = True

    return render_template(
        "index.html",
        resultados=resultados,
        sin_stock=sin_stock,
        proveedores=proveedores,
        fuentes=fuentes,
        fecha_actualizacion=fecha_actualizacion,
        current_q=current_q,
        current_proveedor=current_proveedor,
        current_sort=current_sort,
        page=page,
        per_page=per_page,
        total_count=total_count,
        total_pages=total_pages
    )

@app.route('/export_cart', methods=['POST'])
@login_required
def export_cart():
    cart_data = request.get_json()
    if not cart_data:
        return {'error': 'No cart data provided'}, 400

    # Crear workbook Excel
    wb = Workbook()
    
    # Hoja principal
    ws_main = wb.active
    ws_main.title = "Lista de Compras"
    
    # Agregar fecha y hora
    now = datetime.now()
    ws_main['A1'] = f'Fecha y hora: {now.strftime("%d/%m/%Y %H:%M")}'
    ws_main['A1'].font = Font(bold=True)
    
    # Headers
    ws_main['A3'] = 'Fuente'
    ws_main['B3'] = 'Producto'
    ws_main['C3'] = 'Cantidad'
    for cell in ['A3', 'B3', 'C3']:
        ws_main[cell].font = Font(bold=True)
        ws_main[cell].alignment = Alignment(horizontal='center')
    
    # Agrupar por fuente (usando solo el nombre principal)
    fuentes = {}
    total_general = 0

    for item in cart_data:
        fuente_main = item['fuente'].split(' | ')[0]
        if fuente_main not in fuentes:
            fuentes[fuente_main] = []
        fuentes[fuente_main].append(item)
        total_general += item['subtotal']

    # Llenar la hoja principal
    row = 4
    for fuente, items in fuentes.items():
        # Encabezado de fuente
        ws_main[f'A{row}'] = fuente
        ws_main[f'A{row}'].font = Font(bold=True)
        row += 1
        
        for item in items:
            ws_main[f'B{row}'] = item['nombre']
            ws_main[f'C{row}'] = item['cantidad']
            row += 1
        
        row += 1  # Espacio entre grupos

    # Total general
    ws_main[f'A{row}'] = 'TOTAL GENERAL'
    ws_main[f'A{row}'].font = Font(bold=True)
    ws_main[f'C{row}'] = f'S/ {total_general:.2f}'
    row += 1

    # Hoja de proveedores
    ws_prov = wb.create_sheet("Proveedores")
    ws_prov['A1'] = 'Producto'
    ws_prov['B1'] = 'Cantidad'
    ws_prov['C1'] = 'Proveedor'
    for cell in ['A1', 'B1', 'C1']:
        ws_prov[cell].font = Font(bold=True)
        ws_prov[cell].alignment = Alignment(horizontal='center')
    
    row = 2
    for item in cart_data:
        ws_prov[f'A{row}'] = item['nombre']
        ws_prov[f'B{row}'] = item['cantidad']
        ws_prov[f'C{row}'] = item['proveedor']
        row += 1

    # Ajustar ancho de columnas
    for ws in [ws_main, ws_prov]:
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 40
        ws.column_dimensions['C'].width = 15

    # Guardar en memoria
    bio = BytesIO()
    wb.save(bio)
    bio.seek(0)

    return send_file(bio, as_attachment=True, download_name='lista_compras.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == "__main__":
    app.run(debug=True)

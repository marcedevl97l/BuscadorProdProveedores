from flask import Flask, render_template, request, session, redirect, url_for, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from config import DB
from datetime import datetime
from docx import Document
from docx.shared import Inches
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_this_in_production'

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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

@app.route('/export_cart', methods=['POST'])
@login_required
def export_cart():
    cart_data = request.get_json()
    if not cart_data:
        return {'error': 'No cart data provided'}, 400

    # Crear documento Word
    doc = Document()
    doc.add_heading('Lista de Compras', 0)

    # Agregar fecha y hora
    now = datetime.now()
    doc.add_paragraph(f'Fecha y hora: {now.strftime("%d/%m/%Y %H:%M")}')

    # Agrupar por fuente
    fuentes = {}
    total_general = 0

    for item in cart_data:
        fuente = item['fuente']
        if fuente not in fuentes:
            fuentes[fuente] = []
        fuentes[fuente].append(item)
        total_general += item['subtotal']

    # Crear tabla para cada fuente
    for fuente, items in fuentes.items():
        doc.add_heading(f'Fuente: {fuente}', level=1)
        
        table = doc.add_table(rows=1, cols=4)
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Producto'
        hdr_cells[1].text = 'Cantidad'
        hdr_cells[2].text = 'Precio Unit.'
        hdr_cells[3].text = 'Subtotal'

        total_fuente = 0
        for item in items:
            row_cells = table.add_row().cells
            row_cells[0].text = item['nombre']
            row_cells[1].text = str(item['cantidad'])
            row_cells[2].text = f"S/ {item['precio']:.2f}"
            row_cells[3].text = f"S/ {item['subtotal']:.2f}"
            total_fuente += item['subtotal']

        # Total por fuente
        row_cells = table.add_row().cells
        row_cells[0].text = 'TOTAL'
        row_cells[1].text = ''
        row_cells[2].text = ''
        row_cells[3].text = f"S/ {total_fuente:.2f}"

    # Total general
    doc.add_paragraph('')
    doc.add_paragraph(f'TOTAL GENERAL: S/ {total_general:.2f}')

    # Guardar en memoria
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)

    return send_file(bio, as_attachment=True, download_name='lista_compras.docx', mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

if __name__ == "__main__":
    app.run(debug=True)

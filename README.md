# Buscador de Productos — Proyecto organizado

Instrucciones rápidas:

- Instalar dependencias:

```bash
pip install -r requirements.txt
```

- (Playwright) instalar navegadores si usas `scraper_farmacom.py`:

```bash
playwright install
```

- Inicializar base de datos (crea `db.sqlite` con la tabla `productos`):

```bash
python init_db.py
```

- Ejecutar la app web (Flask):

```bash
python app.py
# Abrir http://localhost:5000
```

Notas:
- La configuración central está en `config.py` (ruta de la BD `DB`).
- Se movió la base de datos antigua a `data/legacy_productos.db` y se eliminaron scripts redundantes (`cargar_web.py`, `cargar_farmacom.py`).

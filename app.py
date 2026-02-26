from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'leon-microsaas-secret-2024'

DB_PATH = 'microsaas.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT,
        telefono TEXT,
        direccion TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        precio REAL NOT NULL DEFAULT 0,
        stock INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        estado TEXT DEFAULT 'pendiente',
        notas TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS lineas_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER NOT NULL,
        producto_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL DEFAULT 1,
        precio_unitario REAL NOT NULL,
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    )''')
    # Default user
    try:
        c.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", ('leon', 'leon'))
    except:
        pass
    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ── AUTH ─────────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'usuario' in session:
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM usuarios WHERE username=? AND password=?', (username, password)).fetchone()
        conn.close()
        if user:
            session['usuario'] = username
            return redirect(url_for('dashboard'))
        else:
            error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    stats = {
        'clientes': conn.execute('SELECT COUNT(*) FROM clientes').fetchone()[0],
        'productos': conn.execute('SELECT COUNT(*) FROM productos').fetchone()[0],
        'pedidos': conn.execute('SELECT COUNT(*) FROM pedidos').fetchone()[0],
    }
    conn.close()
    return render_template('dashboard.html', active='dashboard', stats=stats)

# ── CLIENTES ─────────────────────────────────────────────────────────────────

@app.route('/clientes')
@login_required
def clientes():
    conn = get_db()
    lista = conn.execute('SELECT * FROM clientes ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('clientes.html', active='clientes', clientes=lista)

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_cliente():
    if request.method == 'POST':
        conn = get_db()
        conn.execute('INSERT INTO clientes (nombre, email, telefono, direccion) VALUES (?,?,?,?)',
            (request.form['nombre'], request.form['email'], request.form['telefono'], request.form['direccion']))
        conn.commit()
        conn.close()
        return redirect(url_for('clientes'))
    return render_template('cliente_form.html', active='clientes', cliente=None)

@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    conn = get_db()
    if request.method == 'POST':
        conn.execute('UPDATE clientes SET nombre=?, email=?, telefono=?, direccion=? WHERE id=?',
            (request.form['nombre'], request.form['email'], request.form['telefono'], request.form['direccion'], id))
        conn.commit()
        conn.close()
        return redirect(url_for('clientes'))
    cliente = conn.execute('SELECT * FROM clientes WHERE id=?', (id,)).fetchone()
    conn.close()
    return render_template('cliente_form.html', active='clientes', cliente=cliente)

@app.route('/clientes/eliminar/<int:id>')
@login_required
def eliminar_cliente(id):
    conn = get_db()
    conn.execute('DELETE FROM clientes WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('clientes'))

# ── PRODUCTOS ─────────────────────────────────────────────────────────────────

@app.route('/productos')
@login_required
def productos():
    conn = get_db()
    lista = conn.execute('SELECT * FROM productos ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('productos.html', active='productos', productos=lista)

@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    if request.method == 'POST':
        conn = get_db()
        conn.execute('INSERT INTO productos (nombre, descripcion, precio, stock) VALUES (?,?,?,?)',
            (request.form['nombre'], request.form['descripcion'], float(request.form['precio']), int(request.form['stock'])))
        conn.commit()
        conn.close()
        return redirect(url_for('productos'))
    return render_template('producto_form.html', active='productos', producto=None)

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    conn = get_db()
    if request.method == 'POST':
        conn.execute('UPDATE productos SET nombre=?, descripcion=?, precio=?, stock=? WHERE id=?',
            (request.form['nombre'], request.form['descripcion'], float(request.form['precio']), int(request.form['stock']), id))
        conn.commit()
        conn.close()
        return redirect(url_for('productos'))
    producto = conn.execute('SELECT * FROM productos WHERE id=?', (id,)).fetchone()
    conn.close()
    return render_template('producto_form.html', active='productos', producto=producto)

@app.route('/productos/eliminar/<int:id>')
@login_required
def eliminar_producto(id):
    conn = get_db()
    conn.execute('DELETE FROM productos WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('productos'))

# ── PEDIDOS ─────────────────────────────────────────────────────────────────

@app.route('/pedidos')
@login_required
def pedidos():
    conn = get_db()
    lista = conn.execute('''
        SELECT p.*, c.nombre as cliente_nombre,
               (SELECT SUM(lp.cantidad * lp.precio_unitario) FROM lineas_pedido lp WHERE lp.pedido_id = p.id) as total
        FROM pedidos p
        JOIN clientes c ON p.cliente_id = c.id
        ORDER BY p.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('pedidos.html', active='pedidos', pedidos=lista)

@app.route('/pedidos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_pedido():
    conn = get_db()
    if request.method == 'POST':
        cliente_id = request.form['cliente_id']
        estado = request.form['estado']
        notas = request.form['notas']
        cur = conn.execute('INSERT INTO pedidos (cliente_id, estado, notas) VALUES (?,?,?)', (cliente_id, estado, notas))
        pedido_id = cur.lastrowid
        productos_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')
        precios = request.form.getlist('precio_unitario[]')
        for pid, cant, precio in zip(productos_ids, cantidades, precios):
            if pid and cant and precio:
                conn.execute('INSERT INTO lineas_pedido (pedido_id, producto_id, cantidad, precio_unitario) VALUES (?,?,?,?)',
                    (pedido_id, int(pid), int(cant), float(precio)))
        conn.commit()
        conn.close()
        return redirect(url_for('pedidos'))
    clientes_lista = conn.execute('SELECT * FROM clientes ORDER BY nombre').fetchall()
    productos_lista = conn.execute('SELECT * FROM productos ORDER BY nombre').fetchall()
    conn.close()
    return render_template('pedido_form.html', active='pedidos', pedido=None, clientes=clientes_lista, productos=productos_lista, lineas=[])

@app.route('/pedidos/ver/<int:id>')
@login_required
def ver_pedido(id):
    conn = get_db()
    pedido = conn.execute('''
        SELECT p.*, c.nombre as cliente_nombre, c.email as cliente_email
        FROM pedidos p JOIN clientes c ON p.cliente_id = c.id WHERE p.id=?
    ''', (id,)).fetchone()
    lineas = conn.execute('''
        SELECT lp.*, pr.nombre as producto_nombre
        FROM lineas_pedido lp JOIN productos pr ON lp.producto_id = pr.id
        WHERE lp.pedido_id=?
    ''', (id,)).fetchall()
    conn.close()
    total = sum(l['cantidad'] * l['precio_unitario'] for l in lineas)
    return render_template('pedido_ver.html', active='pedidos', pedido=pedido, lineas=lineas, total=total)

@app.route('/pedidos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_pedido(id):
    conn = get_db()
    if request.method == 'POST':
        conn.execute('UPDATE pedidos SET cliente_id=?, estado=?, notas=? WHERE id=?',
            (request.form['cliente_id'], request.form['estado'], request.form['notas'], id))
        conn.execute('DELETE FROM lineas_pedido WHERE pedido_id=?', (id,))
        productos_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')
        precios = request.form.getlist('precio_unitario[]')
        for pid, cant, precio in zip(productos_ids, cantidades, precios):
            if pid and cant and precio:
                conn.execute('INSERT INTO lineas_pedido (pedido_id, producto_id, cantidad, precio_unitario) VALUES (?,?,?,?)',
                    (id, int(pid), int(cant), float(precio)))
        conn.commit()
        conn.close()
        return redirect(url_for('pedidos'))
    pedido = conn.execute('SELECT * FROM pedidos WHERE id=?', (id,)).fetchone()
    lineas = conn.execute('''
        SELECT lp.*, pr.nombre as producto_nombre
        FROM lineas_pedido lp JOIN productos pr ON lp.producto_id = pr.id WHERE lp.pedido_id=?
    ''', (id,)).fetchall()
    clientes_lista = conn.execute('SELECT * FROM clientes ORDER BY nombre').fetchall()
    productos_lista = conn.execute('SELECT * FROM productos ORDER BY nombre').fetchall()
    conn.close()
    return render_template('pedido_form.html', active='pedidos', pedido=pedido, clientes=clientes_lista, productos=productos_lista, lineas=lineas)

@app.route('/pedidos/eliminar/<int:id>')
@login_required
def eliminar_pedido(id):
    conn = get_db()
    conn.execute('DELETE FROM lineas_pedido WHERE pedido_id=?', (id,))
    conn.execute('DELETE FROM pedidos WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('pedidos'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

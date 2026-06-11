import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = 'entrevistas-secret-key'

DB_PATH = 'entrevistas.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS entrevistas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            nombre_negocio TEXT NOT NULL,
            nombre_contacto TEXT,
            telefono TEXT,
            email TEXT,
            tipo_negocio TEXT,
            problema_1 INTEGER,
            problema_2 INTEGER,
            problema_3 INTEGER,
            problema_4 INTEGER,
            problema_5 INTEGER,
            senal_compromiso TEXT,
            senal_fecha TEXT,
            senal_presupuesto TEXT,
            notas TEXT,
            link_audio TEXT,
            estado TEXT DEFAULT 'pendiente',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    entrevistas = conn.execute('SELECT * FROM entrevistas ORDER BY fecha DESC').fetchall()
    total = len(entrevistas)
    si = len([e for e in entrevistas if e['senal_compromiso'] == 'SI'])
    no = len([e for e in entrevistas if e['senal_compromiso'] == 'NO'])
    quizas = len([e for e in entrevistas if e['senal_compromiso'] == 'QUIZAS'])
    conn.close()
    return render_template('index.html', entrevistas=entrevistas, 
                         stats={'total': total, 'si': si, 'no': no, 'quizas': quizas})

@app.route('/nueva', methods=['GET', 'POST'])
def nueva():
    if request.method == 'POST':
        conn = sqlite3.connect(DB_PATH)
        conn.execute('''
            INSERT INTO entrevistas 
            (fecha, nombre_negocio, nombre_contacto, telefono, email, tipo_negocio,
             problema_1, problema_2, problema_3, problema_4, problema_5,
             senal_compromiso, senal_fecha, senal_presupuesto, notas, link_audio, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.form.get('fecha', datetime.now().strftime('%Y-%m-%d')),
            request.form.get('nombre_negocio'),
            request.form.get('nombre_contacto'),
            request.form.get('telefono'),
            request.form.get('email'),
            request.form.get('tipo_negocio'),
            request.form.get('problema_1', 3),
            request.form.get('problema_2', 3),
            request.form.get('problema_3', 3),
            request.form.get('problema_4', 3),
            request.form.get('problema_5', 3),
            request.form.get('senal_compromiso', 'QUIZAS'),
            request.form.get('senal_fecha'),
            request.form.get('senal_presupuesto'),
            request.form.get('notas'),
            request.form.get('link_audio'),
            request.form.get('estado', 'pendiente')
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('nueva.html', hoy=datetime.now().strftime('%Y-%m-%d'))

@app.route('/ver/<int:id>')
def ver(id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    entrevista = conn.execute('SELECT * FROM entrevistas WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('ver.html', e=entrevista)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    if request.method == 'POST':
        conn.execute('''
            UPDATE entrevistas SET
            fecha = ?, nombre_negocio = ?, nombre_contacto = ?, telefono = ?, email = ?, tipo_negocio = ?,
            problema_1 = ?, problema_2 = ?, problema_3 = ?, problema_4 = ?, problema_5 = ?,
            senal_compromiso = ?, senal_fecha = ?, senal_presupuesto = ?, notas = ?, link_audio = ?, estado = ?
            WHERE id = ?
        ''', (
            request.form.get('fecha'), request.form.get('nombre_negocio'),
            request.form.get('nombre_contacto'), request.form.get('telefono'),
            request.form.get('email'), request.form.get('tipo_negocio'),
            request.form.get('problema_1'), request.form.get('problema_2'),
            request.form.get('problema_3'), request.form.get('problema_4'),
            request.form.get('problema_5'), request.form.get('senal_compromiso'),
            request.form.get('senal_fecha'), request.form.get('senal_presupuesto'),
            request.form.get('notas'), request.form.get('link_audio'),
            request.form.get('estado'), id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for('ver', id=id))
    entrevista = conn.execute('SELECT * FROM entrevistas WHERE id = ?', (id,)).fetchone()
    conn.close()
    return render_template('editar.html', e=entrevista)

@app.route('/eliminar/<int:id>')
def eliminar(id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM entrevistas WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)

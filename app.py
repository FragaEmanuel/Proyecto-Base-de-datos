from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import Database
import datetime

app = Flask(__name__)
db = Database()

@app.route('/')
def index():
    return render_template('index.html')

# ABM de Participantes
@app.route('/participantes')
def participantes():
    query = """
    SELECT p.ci, p.nombre, p.apellido, p.email, 
           GROUP_CONCAT(DISTINCT ppa.nombre_programa) as programas
    FROM participante p
    LEFT JOIN participante_programa_académico ppa ON p.ci = ppa.ci_participante
    GROUP BY p.ci
    """
    participantes = db.execute_query(query)
    return render_template('participantes.html', participantes=participantes)

@app.route('/participante/nuevo', methods=['GET', 'POST'])
def nuevo_participante():
    if request.method == 'POST':
        ci = request.form['ci']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        
        query = "INSERT INTO participante (ci, nombre, apellido, email) VALUES (%s, %s, %s, %s)"
        result = db.execute_insert(query, (ci, nombre, apellido, email))
        
        if result:
            return redirect(url_for('participantes'))
    
    return render_template('nuevo_participante.html')

# ABM de Salas
@app.route('/salas')
def salas():
    query = """
    SELECT s.nombre_sala, s.edificio, s.capacidad, s.tipo_sala, 
           e.direccion, e.departamento
    FROM sala s
    JOIN edificio e ON s.edificio = e.nombre_edificio
    """
    salas = db.execute_query(query)
    return render_template('salas.html', salas=salas)

# Reservas
@app.route('/reservas')
def reservas():
    query = """
    SELECT r.id_reserva, r.nombre_sala, r.edificio, r.fecha, 
           t.hora_inicio, t.hora_fin, r.estado,
           COUNT(rp.ci_participante) as participantes
    FROM reserva r
    JOIN turno t ON r.id_turno = t.id_turno
    LEFT JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
    GROUP BY r.id_reserva
    """
    reservas = db.execute_query(query)
    return render_template('reservas.html', reservas=reservas)

@app.route('/reserva/nueva', methods=['GET', 'POST'])
def nueva_reserva():
    if request.method == 'POST':
        # Aquí implementarías la lógica de reserva con validaciones
        pass
    
    # Obtener datos para el formulario
    salas = db.execute_query("SELECT nombre_sala, edificio, capacidad FROM sala")
    turnos = db.execute_query("SELECT id_turno, hora_inicio, hora_fin FROM turno")
    participantes = db.execute_query("SELECT ci, nombre, apellido FROM participante")
    
    return render_template('nueva_reserva.html', 
                         salas=salas, 
                         turnos=turnos, 
                         participantes=participantes)

# Reportes
@app.route('/reportes')
def reportes():
    # Salas más reservadas
    query_salas_populares = """
    SELECT r.nombre_sala, r.edificio, COUNT(*) as total_reservas
    FROM reserva r
    WHERE r.estado = 'activa'
    GROUP BY r.nombre_sala, r.edificio
    ORDER BY total_reservas DESC
    LIMIT 10
    """
    salas_populares = db.execute_query(query_salas_populares)
    
    # Turnos más demandados
    query_turnos_demandados = """
    SELECT t.hora_inicio, t.hora_fin, COUNT(*) as total_reservas
    FROM reserva r
    JOIN turno t ON r.id_turno = t.id_turno
    WHERE r.estado = 'activa'
    GROUP BY t.id_turno
    ORDER BY total_reservas DESC
    """
    turnos_demandados = db.execute_query(query_turnos_demandados)
    
    return render_template('reportes.html', 
                         salas_populares=salas_populares,
                         turnos_demandados=turnos_demandados)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
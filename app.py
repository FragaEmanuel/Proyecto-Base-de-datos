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

# Participante Nuevo
@app.route('/participante/nuevo', methods=['GET', 'POST'])
def nuevo_participante():
    if request.method == 'POST':
        ci = request.form['ci']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        
        query = "INSERT INTO participante (ci, nombre, apellido, email) VALUES (%s, %s, %s, %s)"
        db.execute_insert(query, (ci, nombre, apellido, email))

        # Redirigir SIEMPRE después del insert
        return redirect(url_for('participantes'))
    
    return render_template('nuevo_participante.html')

@app.route('/participante/eliminar/<string:ci>', methods=['POST'])
def eliminar_participante(ci):
    query = "DELETE FROM participante WHERE ci = %s"
    db.execute_insert(query, (ci,))
    
    return redirect(url_for('participantes'))

@app.route('/participante/editar/<string:ci>', methods=['GET', 'POST'])
def editar_participante(ci):
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']

        query = "UPDATE participante SET nombre=%s, apellido=%s, email=%s WHERE ci=%s"
        db.execute_insert(query, (nombre, apellido, email, ci))

        return redirect(url_for('participantes'))

    query = "SELECT ci, nombre, apellido, email FROM participante WHERE ci = %s"
    participante = db.execute_query(query, (ci,))

    if participante:
        return render_template('editar_participante.html', participante=participante[0])
    else:
        return "Participante no encontrado", 404

# Listar Salas
@app.route('/salas')
def salas():
    query = """
    SELECT s.nombre_sala, s.edificio, s.capacidad, s.tipo_sala, 
           e.direccion, e.departamento
    FROM sala s
    JOIN edificio e ON s.edificio = e.nombre_edificio
    ORDER BY s.edificio, s.nombre_sala
    """
    salas = db.execute_query(query)
    return render_template('salas.html', salas=salas)

#ABM de Salas
@app.route('/sala/nueva', methods=['GET', 'POST'])
def nueva_sala():
    if request.method == 'POST':
        nombre_sala = request.form['nombre_sala']
        edificio = request.form['edificio']
        capacidad = request.form['capacidad']
        tipo_sala = request.form['tipo_sala']
        
        query = "INSERT INTO sala (nombre_sala, edificio, capacidad, tipo_sala) VALUES (%s, %s, %s, %s)"
        result = db.execute_insert(query, (nombre_sala, edificio, capacidad, tipo_sala))
        
        if result:
            return redirect(url_for('salas'))
    
    edificios = db.execute_query("SELECT nombre_edificio FROM edificio")
    return render_template('nueva_sala.html', edificios=edificios)

@app.route('/sala/eliminar/<string:nombre_sala>/<string:edificio>', methods=['POST'])
def eliminar_sala(nombre_sala, edificio):
    query = "DELETE FROM sala WHERE nombre_sala = %s AND edificio = %s"
    result = db.execute_insert(query, (nombre_sala, edificio))
    
    return redirect(url_for('salas'))

# ABM de Reservas

# Listar Reservas
@app.route('/reservas')
def reservas():
    query = """
    SELECT r.id_reserva, r.nombre_sala, r.edificio, r.fecha, 
           t.hora_inicio, t.hora_fin, r.estado,
           GROUP_CONCAT(CONCAT(p.nombre, ' ', p.apellido) SEPARATOR ', ') AS participantes
    FROM reserva r
    JOIN turno t ON r.id_turno = t.id_turno
    LEFT JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
    LEFT JOIN participante p ON rp.ci_participante = p.ci
    GROUP BY r.id_reserva
    ORDER BY r.fecha DESC, t.hora_inicio ASC
    """
    reservas = db.execute_query(query)
    return render_template('reservas.html', reservas=reservas)


@app.route('/reserva/nueva', methods=['GET', 'POST'])
def nueva_reserva():
    if request.method == 'POST':
        # Tomar datos del formulario
        nombre_sala = request.form['sala']
        edificio = request.form['edificio']
        fecha = request.form['fecha']
        id_turno = request.form['turno']
        participantes = request.form.getlist('participantes')

        # Insertar reserva
        query = "INSERT INTO reserva (nombre_sala, edificio, fecha, id_turno, estado) VALUES (%s, %s, %s, %s, 'activa')"
        reserva_id = db.execute_insert(query, (nombre_sala, edificio, fecha, id_turno))
        
        # Insertar participantes asociados
        for ci in participantes:
            query_part = "INSERT INTO reserva_participante (id_reserva, ci_participante) VALUES (%s, %s)"
            db.execute_insert(query_part, (reserva_id, ci))
        
        # Redirigir sin mostrar flash
        return redirect(url_for('reservas'))

    # Obtener datos para el formulario
    salas = db.execute_query("SELECT nombre_sala, edificio, capacidad FROM sala")
    turnos = db.execute_query("SELECT id_turno, hora_inicio, hora_fin FROM turno")
    participantes = db.execute_query("SELECT ci, nombre, apellido FROM participante")
    
    return render_template('nueva_reserva.html', 
                           salas=salas, 
                           turnos=turnos, 
                           participantes=participantes)
    
@app.route('/reserva/cancelar/<int:id_reserva>', methods=['POST'])
def cancelar_reserva(id_reserva):
    query = "UPDATE reserva SET estado = 'cancelada' WHERE id_reserva = %s"
    db.execute_insert(query, (id_reserva,))
    return redirect(url_for('reservas'))



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
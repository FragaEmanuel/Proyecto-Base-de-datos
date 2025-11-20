from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import Database
import datetime

app = Flask(__name__)
db = Database()

@app.route('/')
def index():
    total_salas = db.execute_query("SELECT COUNT(*) AS total FROM sala")[0]['total']
    total_participantes = db.execute_query("SELECT COUNT(*) AS total FROM participante")[0]['total']
    reservas_activas = db.execute_query("SELECT COUNT(*) AS total FROM reserva WHERE estado = 'activa'")[0]['total']
    sanciones_activas = db.execute_query("""
        SELECT COUNT(*) AS total 
        FROM sancion_participante
        WHERE fecha_fin >= CURDATE()
    """)[0]['total']

    reservas_recientes = db.execute_query("""
        SELECT r.id_reserva, r.nombre_sala, r.edificio, r.fecha,
               t.hora_inicio, t.hora_fin,
               r.estado,
               GROUP_CONCAT(CONCAT(p.nombre, ' ', p.apellido) SEPARATOR ', ') AS participantes
        FROM reserva r
        JOIN turno t ON r.id_turno = t.id_turno
        LEFT JOIN reserva_participante rp ON r.id_reserva = rp.id_reserva
        LEFT JOIN participante p ON rp.ci_participante = p.ci
        GROUP BY r.id_reserva
        ORDER BY r.fecha DESC, t.hora_inicio DESC
        LIMIT 10
    """)

    return render_template(
        'index.html',
        total_salas=total_salas,
        total_participantes=total_participantes,
        reservas_activas=reservas_activas,
        sanciones_activas=sanciones_activas,
        reservas_recientes=reservas_recientes
    )

# ABM de Participantes
@app.route('/participantes')
def participantes():
    query = """
    SELECT p.ci, p.nombre, p.apellido, p.email, 
           GROUP_CONCAT(DISTINCT ppa.nombre_programa) as programas
    FROM participante p
    LEFT JOIN participante_programa_academico ppa ON p.ci = ppa.ci_participante
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

        programas = request.form.getlist('programas')
        rol = request.form['rol']

        #Inserta participante
        query = """
            INSERT INTO participante (ci, nombre, apellido, email)
            VALUES (%s, %s, %s, %s)
        """
        db.execute_insert(query, (ci, nombre, apellido, email))

        #Inserta relación con sus programas académicos
        query_prog = """
            INSERT INTO participante_programa_academico 
            (ci_participante, nombre_programa, rol)
            VALUES (%s, %s, %s)
        """

        for prog in programas:
            db.execute_insert(query_prog, (ci, prog, rol))

        return redirect(url_for('participantes'))

    programas = db.execute_query("SELECT nombre_programa, tipo FROM programa_academico")
    return render_template('nuevo_participante.html', programas=programas)

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
        programas = request.form.getlist('programas')
        rol = request.form['rol']

        #Actualizar participante
        db.execute_insert("""
            UPDATE participante
            SET nombre=%s, apellido=%s, email=%s
            WHERE ci=%s
        """, (nombre, apellido, email, ci))

        #Borrar asociaciones anteriores
        db.execute_insert("""
            DELETE FROM participante_programa_academico
            WHERE ci_participante = %s
        """, (ci,))

        #Insertar las nuevas asociaciones
        for p in programas:
            db.execute_insert("""
                INSERT INTO participante_programa_academico 
                (ci_participante, nombre_programa, rol)
                VALUES (%s, %s, %s)
            """, (ci, p, rol))

        return redirect(url_for('participantes'))

    participante = db.execute_query(
        "SELECT ci, nombre, apellido, email FROM participante WHERE ci=%s",
        (ci,)
    )[0]

    #Programas disponibles
    programas = db.execute_query("""
        SELECT nombre_programa, tipo 
        FROM programa_academico
    """)

    # Programas actuales del participante
    programas_participante_rows = db.execute_query("""
        SELECT nombre_programa 
        FROM participante_programa_academico 
        WHERE ci_participante = %s
    """, (ci,))

    programas_participante = [p['nombre_programa'] 
                              for p in programas_participante_rows]

    # Obtener rol actual
    rol_actual_row = db.execute_query("""
        SELECT rol 
        FROM participante_programa_academico 
        WHERE ci_participante = %s
        LIMIT 1
    """, (ci,))

    rol_actual = rol_actual_row[0]['rol'] if rol_actual_row else "alumno"

    return render_template(
        'editar_participante.html',
        participante=participante,
        programas=programas,
        programas_participante=programas_participante,
        rol_actual=rol_actual
    )

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

@app.route('/sala/editar/<string:nombre_sala>/<string:edificio>', methods=['GET', 'POST'])
def editar_sala(nombre_sala, edificio):

    if request.method == 'POST':
        capacidad = request.form['capacidad']
        tipo_sala = request.form['tipo_sala']

        db.execute_insert("""
            UPDATE sala
            SET capacidad = %s, tipo_sala = %s
            WHERE nombre_sala = %s AND edificio = %s
        """, (capacidad, tipo_sala, nombre_sala, edificio))

        return redirect(url_for('salas'))

    sala = db.execute_query("""
        SELECT * FROM sala 
        WHERE nombre_sala=%s AND edificio=%s
    """, (nombre_sala, edificio))[0]

    return render_template("editar_sala.html", sala=sala)

@app.route('/sala/eliminar/<string:nombre_sala>/<string:edificio>', methods=['POST'])
def eliminar_sala(nombre_sala, edificio):
    db.execute_insert("""
        DELETE FROM sala 
        WHERE nombre_sala = %s AND edificio = %s
    """, (nombre_sala, edificio))

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

        print("Voy a insertar reserva:", nombre_sala, edificio, fecha, id_turno)

        reserva_id = db.execute_insert(query, (nombre_sala, edificio, fecha, id_turno))

        print("ID obtenido:", reserva_id)
        
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
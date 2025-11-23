from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import Database
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from validaciones import (
    validar_tipo_sala,
    horas_reservadas_en_dia,
    reservas_activas_en_semana,
    tiene_solapamiento
)

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

        sala = request.form['sala']
        edificio = request.form['edificio']
        fecha = request.form['fecha']
        id_turno = request.form['turno']
        participantes = request.form.getlist('participantes')

        # Info de sala
        info = db.execute_query("""
            SELECT capacidad, tipo_sala
            FROM sala
            WHERE nombre_sala=%s AND edificio=%s
        """, (sala, edificio))[0]

        capacidad = info["capacidad"]
        tipo_sala = info["tipo_sala"]

        # === VALIDACIONES GENERALES ===

        # 1) Sala ya reservada → error
        if sala_ocupada(sala, edificio, fecha, id_turno):
            return "ERROR: La sala ya está reservada para ese turno."


        # 2) Capacidad insuficiente → error (solo una vez, no dentro del loop)
        if len(participantes) > capacidad:
            return "ERROR: La cantidad de participantes excede la capacidad de la sala."

        # === VALIDACIONES POR PARTICIPANTE ===
        for ci in participantes:

            # 3) Participante sancionado
            if esta_sancionado(ci, fecha):
                return f"ERROR: El participante {ci} está sancionado y no puede reservar."

            # 4) Tipo de sala no permitido
            if not validar_tipo_sala(ci, tipo_sala):
                return f"ERROR: El participante {ci} no tiene permisos para este tipo de sala ({tipo_sala})."

            # 5) Solapamiento de turnos
            if tiene_solapamiento(ci, fecha, id_turno):
                return f"ERROR: El participante {ci} ya tiene una reserva en ese turno."

            # 6) Máximo de 2 horas por día
            if horas_reservadas_en_dia(ci, fecha, edificio) >= 2:
                return f"ERROR: El participante {ci} ya alcanzó el máximo diario (2 horas)."

            # 7) Máximo de 3 reservas por semana
            if reservas_activas_en_semana(ci, fecha) >= 3:
                return f"ERROR: El participante {ci} ya alcanzó el máximo semanal (3 reservas)."

        # INSERTAR RESERVA
        reserva_id = db.execute_insert("""
            INSERT INTO reserva (nombre_sala, edificio, fecha, id_turno, estado)
            VALUES (%s, %s, %s, %s, 'activa')
        """, (sala, edificio, fecha, id_turno))

        # ASOCIAR PARTICIPANTES
        for ci in participantes:
            db.execute_insert("""
                INSERT INTO reserva_participante (id_reserva, ci_participante)
                VALUES (%s, %s)
            """, (reserva_id, ci))

        return redirect(url_for('reservas'))

    # GET — formulario
    salas = db.execute_query("SELECT nombre_sala, edificio, capacidad FROM sala")
    turnos = db.execute_query("SELECT id_turno, hora_inicio, hora_fin FROM turno")
    participantes = db.execute_query("SELECT ci, nombre, apellido FROM participante")

    return render_template(
        'nueva_reserva.html',
        salas=salas,
        turnos=turnos,
        participantes=participantes
    )
    
@app.route('/reserva/cancelar/<int:id_reserva>', methods=['POST'])
def cancelar_reserva(id_reserva):
    query = "UPDATE reserva SET estado = 'cancelada' WHERE id_reserva = %s"
    db.execute_insert(query, (id_reserva,))
    return redirect(url_for('reservas'))

@app.route('/reserva/editar/<int:id_reserva>', methods=['GET', 'POST'])
def editar_reserva(id_reserva):

    # --- OBTENER INFO BASE ---
    reserva = db.execute_query("""
        SELECT r.id_reserva, r.nombre_sala, r.edificio, r.fecha, r.id_turno,
               t.hora_inicio, t.hora_fin
        FROM reserva r
        JOIN turno t ON r.id_turno = t.id_turno
        WHERE r.id_reserva = %s
    """, (id_reserva,))[0]

    sala = reserva["nombre_sala"]
    edificio = reserva["edificio"]

    # INFO sala (capacidad + tipo)
    info_sala = db.execute_query("""
        SELECT capacidad, tipo_sala
        FROM sala
        WHERE nombre_sala=%s AND edificio=%s
    """, (sala, edificio))[0]

    capacidad = info_sala["capacidad"]
    tipo_sala = info_sala["tipo_sala"]

    # PARTICIPANTES actuales
    participantes_actuales = db.execute_query("""
        SELECT ci_participante
        FROM reserva_participante
        WHERE id_reserva = %s
    """, (id_reserva,))
    participantes_actuales = [p["ci_participante"] for p in participantes_actuales]

    # --- POST: guardar ---
    if request.method == "POST":
        fecha = request.form["fecha"]
        turno = request.form["turno"]
        participantes = request.form.getlist("participantes")

        # VALIDACIÓN: sala ocupada
        if sala_ocupada_editando(sala, edificio, fecha, turno, id_reserva):
            return "ERROR: La sala ya está reservada en ese turno."

        # VALIDAR UNO POR UNO
        for ci in participantes:

            # Tipo sala
            if not validar_tipo_sala(ci, tipo_sala):
                return f"ERROR: El participante {ci} no puede usar este tipo de sala."

            # Capacidad
            if len(participantes) > capacidad:
                return "ERROR: La cantidad de participantes excede la capacidad."

            # Solapamiento
            if tiene_solapamiento(ci, fecha, turno):
                return f"ERROR: El participante {ci} ya tiene reserva en ese turno."

            # Máximo 2 horas al día
            if horas_reservadas_en_dia(ci, fecha, edificio) >= 2:
                return f"ERROR: El participante {ci} ya alcanzó el máximo diario."

            # Máximo 3 por semana
            if reservas_activas_en_semana(ci, fecha) >= 3:
                return f"ERROR: El participante {ci} alcanzó el máximo semanal."

        # --- ACTUALIZAR RESERVA ---
        db.execute_insert("""
            UPDATE reserva
            SET fecha=%s, id_turno=%s
            WHERE id_reserva=%s
        """, (fecha, turno, id_reserva))

        # --- ACTUALIZAR PARTICIPANTES ---
        db.execute_insert("DELETE FROM reserva_participante WHERE id_reserva=%s", (id_reserva,))

        for ci in participantes:
            db.execute_insert("""
                INSERT INTO reserva_participante (id_reserva, ci_participante)
                VALUES (%s, %s)
            """, (id_reserva, ci))

        return redirect(url_for("reservas"))

    # --- GET: mostrar formulario ---
    turnos = db.execute_query("SELECT id_turno, hora_inicio, hora_fin FROM turno")
    participantes = db.execute_query("SELECT ci, nombre, apellido FROM participante")

    return render_template(
        "editar_reserva.html",
        reserva=reserva,
        turnos=turnos,
        participantes=participantes,
        participantes_actuales=participantes_actuales
    )



# ABM de Sanciones

# Listar Sanciones
@app.route('/sanciones')
def sanciones():
    
    # eliminar vencidas antes de mostrar
    db.execute_insert("""
        DELETE FROM sancion_participante
        WHERE fecha_fin < CURDATE()
    """)
    
    query = """
        SELECT 
            s.id_sancion,
            s.ci_participante,
            s.fecha_inicio,
            s.fecha_fin,
            p.nombre,
            p.apellido
        FROM sancion_participante s
        JOIN participante p ON s.ci_participante = p.ci
        ORDER BY s.fecha_inicio DESC
    """
    
    sanciones = db.execute_query(query)
    current_date = date.today()

    return render_template('sanciones.html', sanciones=sanciones, current_date=current_date)


@app.route('/sancion/nueva', methods=['GET', 'POST'])
def sancion_nueva():
    if request.method == 'POST':
        ci_participante = request.form['ci_participante']
        fecha_inicio = request.form['fecha_inicio']

        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        fecha_fin = fecha_inicio + relativedelta(months=2)


        query = """
            INSERT INTO sancion_participante (ci_participante, fecha_inicio, fecha_fin)
            VALUES (%s, %s, %s)
        """
        db.execute_insert(query, (ci_participante, fecha_inicio, fecha_fin))

        return redirect(url_for('sanciones'))

    participantes = db.execute_query("SELECT ci, nombre, apellido FROM participante")
    return render_template('nueva_sancion.html', participantes=participantes)

@app.route('/sancion/eliminar/<int:id_sancion>', methods=['POST'])
def eliminar_sancion(id_sancion):
    query = "DELETE FROM sancion_participante WHERE id_sancion = %s"
    db.execute_insert(query, (id_sancion,))
    return redirect(url_for('sanciones'))

@app.route('/sancion/editar/<int:id_sancion>', methods=['GET', 'POST'])
def editar_sancion(id_sancion):
    # Obtener sanción actual
    sancion = db.execute_query("""
        SELECT s.id_sancion, s.ci_participante, s.fecha_inicio, s.fecha_fin,
               p.nombre, p.apellido
        FROM sancion_participante s
        JOIN participante p ON s.ci_participante = p.ci
        WHERE id_sancion = %s
    """, (id_sancion,))

    if not sancion:
        return "Sanción no encontrada"

    sancion = sancion[0]

    if request.method == 'POST':
        fecha_inicio = request.form['fecha_inicio']

        fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        fecha_fin_dt = fecha_inicio_dt + relativedelta(months=2)

        db.execute_insert("""
            UPDATE sancion_participante
            SET fecha_inicio = %s,
                fecha_fin = %s
            WHERE id_sancion = %s
        """, (fecha_inicio_dt, fecha_fin_dt, id_sancion))

        return redirect(url_for('sanciones'))

    return render_template('editar_sancion.html', sancion=sancion)


# Reportes
@app.route('/reportes')
def reportes():

    # Salas más reservadas (todas, incluso finalizadas)
    salas_pop = db.execute_query("""
        SELECT r.nombre_sala, r.edificio, COUNT(*) AS total
        FROM reserva r
        GROUP BY r.nombre_sala, r.edificio
        ORDER BY total DESC
        LIMIT 10
    """)

    # Turnos más demandados
    turnos_pop = db.execute_query("""
        SELECT t.hora_inicio, t.hora_fin, COUNT(*) AS total
        FROM reserva r
        JOIN turno t ON r.id_turno = t.id_turno
        GROUP BY t.id_turno
        ORDER BY total DESC
    """)

    # Participantes con más reservas
    partic_reservas = db.execute_query("""
        SELECT p.ci, p.nombre, p.apellido, COUNT(*) AS total
        FROM participante p
        JOIN reserva_participante rp ON p.ci = rp.ci_participante
        GROUP BY p.ci
        ORDER BY total DESC
        LIMIT 10
    """)

    # Salas con mayor porcentaje de ocupación
    ocupacion = db.execute_query("""
        SELECT 
            s.nombre_sala,
            s.edificio,
            COUNT(r.id_reserva) AS reservas,
            s.capacidad
        FROM sala s
        LEFT JOIN reserva r ON s.nombre_sala = r.nombre_sala 
                           AND s.edificio = r.edificio
        GROUP BY s.nombre_sala, s.edificio, s.capacidad
        ORDER BY reservas DESC
    """)

    # Asistencias vs. inasistencias
    asistencia = db.execute_query("""
        SELECT 
            SUM(CASE WHEN asistencia = 1 THEN 1 ELSE 0 END) AS asistencias,
            SUM(CASE WHEN asistencia = 0 THEN 1 ELSE 0 END) AS inasistencias
        FROM reserva_participante
    """)

    return render_template(
        "reportes.html",
        salas_pop=salas_pop,
        turnos_pop=turnos_pop,
        partic_reservas=partic_reservas,
        ocupacion=ocupacion,
        asistencia=asistencia[0]
    )

@app.route('/asistencia/<int:id_reserva>', methods=['GET', 'POST'])
def asistencia(id_reserva):
    if request.method == 'POST':
        # Guardar cambios de asistencia
        asistencias = request.form.getlist('asistencia')

        # Resetear todo
        db.execute_insert("""
            UPDATE reserva_participante
            SET asistencia = 0
            WHERE id_reserva = %s
        """, (id_reserva,))

        # Marcar solo los que asistieron
        for ci in asistencias:
            db.execute_insert("""
                UPDATE reserva_participante
                SET asistencia = 1
                WHERE id_reserva = %s AND ci_participante = %s
            """, (id_reserva, ci))

        # Si todos faltaron → marcar reserva como “sin asistencia”
        cant = db.execute_query("""
            SELECT SUM(asistencia) AS asistentes
            FROM reserva_participante
            WHERE id_reserva = %s
        """, (id_reserva,))[0]['asistentes']

        if cant == 0:
            db.execute_insert("""
                UPDATE reserva
                SET estado = 'sin asistencia'
                WHERE id_reserva = %s
            """, (id_reserva,))
        else:
            db.execute_insert("""
                UPDATE reserva
                SET estado = 'finalizada'
                WHERE id_reserva = %s
            """, (id_reserva,))

        return redirect(url_for('reservas'))

    # GET → mostrar formulario de asistencia

    reserva = db.execute_query("""
        SELECT r.id_reserva, r.nombre_sala, r.edificio, r.fecha,
               t.hora_inicio, t.hora_fin, r.estado
        FROM reserva r
        JOIN turno t ON r.id_turno = t.id_turno
        WHERE r.id_reserva = %s
    """, (id_reserva,))[0]

    participantes = db.execute_query("""
        SELECT rp.ci_participante, p.nombre, p.apellido, rp.asistencia
        FROM reserva_participante rp
        JOIN participante p ON p.ci = rp.ci_participante
        WHERE rp.id_reserva = %s
    """, (id_reserva,))

    return render_template(
        "asistencia.html",
        reserva=reserva,
        participantes=participantes
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
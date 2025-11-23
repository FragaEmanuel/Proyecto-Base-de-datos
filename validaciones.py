from database import Database

db = Database()


# ======================================================
#    OBTENER INFO DE USUARIO (tipo, rol)
# ======================================================
def obtener_info_usuario(ci):
    query = """
        SELECT pa.tipo, ppa.rol
        FROM participante_programa_academico ppa
        JOIN programa_academico pa 
            ON pa.nombre_programa = ppa.nombre_programa
        WHERE ppa.ci_participante = %s
        LIMIT 1
    """
    res = db.execute_query(query, (ci,))
    return res[0] if res else None


# ======================================================
#    VALIDAR SI TIPO DE SALA PERMITE AL USUARIO
# ======================================================
def validar_tipo_sala(ci, tipo_sala):
    info = obtener_info_usuario(ci)
    if not info:
        return False

    tipo = info["tipo"]       # grado / posgrado
    rol = info["rol"]         # alumno / docente

    if tipo_sala == "libre":
        return True

    if tipo_sala == "posgrado" and (tipo == "posgrado" or rol == "docente"):
        return True

    if tipo_sala == "docente" and rol == "docente":
        return True

    return False


# ======================================================
#    VALIDAR SI EL USUARIO ESTÁ SANCIONADO
# ======================================================
def esta_sancionado(ci, fecha):
    query = """
        SELECT COUNT(*) AS total
        FROM sancion_participante
        WHERE ci_participante = %s
        AND fecha_inicio <= %s
        AND fecha_fin >= %s
    """
    result = db.execute_query(query, (ci, fecha, fecha))[0]["total"]
    return result > 0


# ======================================================
#    VALIDAR SI LA SALA YA ESTÁ RESERVADA
# ======================================================
def sala_ocupada(sala, edificio, fecha, turno):
    query = """
        SELECT COUNT(*) AS total
        FROM reserva
        WHERE nombre_sala = %s
        AND edificio = %s
        AND fecha = %s
        AND id_turno = %s
        AND estado = 'activa'
    """
    total = db.execute_query(query, (sala, edificio, fecha, turno))[0]["total"]
    return total > 0


# ======================================================
#    HORAS RESERVADAS EN DÍA (max 2) 
# ======================================================
def horas_reservadas_en_dia(ci, fecha, edificio):
    query = """
        SELECT COUNT(*) AS bloques
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci_participante = %s
        AND r.fecha = %s
        AND r.edificio = %s
        AND r.estado = 'activa'
    """
    return db.execute_query(query, (ci, fecha, edificio))[0]["bloques"]


# ======================================================
#    RESERVAS ACTIVAS DE LA SEMANA (max 3)
# ======================================================
def reservas_activas_en_semana(ci, fecha):
    query = """
        SELECT COUNT(*) AS total
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci_participante = %s
        AND YEARWEEK(r.fecha,1) = YEARWEEK(%s,1)
        AND r.estado = 'activa'
    """
    return db.execute_query(query, (ci, fecha))[0]["total"]


# ======================================================
#    SOLAPAMIENTO DE TURNOS
# ======================================================
def tiene_solapamiento(ci, fecha, turno):
    query = """
        SELECT COUNT(*) AS total
        FROM reserva r
        JOIN reserva_participante rp ON rp.id_reserva = r.id_reserva
        WHERE rp.ci_participante = %s
        AND r.fecha = %s
        AND r.id_turno = %s
        AND r.estado = 'activa'
    """
    return db.execute_query(query, (ci, fecha, turno))[0]["total"] > 0

def sala_ocupada_editando(nombre_sala, edificio, fecha, turno, id_reserva):
    """
    Verifica si una sala ya está reservada en esa fecha y turno,
    EXCLUYENDO la propia reserva en edición.
    """
    query = """
        SELECT COUNT(*) AS total
        FROM reserva
        WHERE nombre_sala = %s
          AND edificio = %s
          AND fecha = %s
          AND id_turno = %s
          AND id_reserva <> %s
          AND estado = 'activa'
    """
    res = db.execute_query(query, (nombre_sala, edificio, fecha, turno, id_reserva))
    return res[0]["total"] > 0

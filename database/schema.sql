CREATE DATABASE IF NOT EXISTS obligatorio;

USE obligatorio;

CREATE TABLE IF NOT EXISTS login (
    correo VARCHAR(50) PRIMARY KEY,
    contraseña VARCHAR(50) NOT NULL
);


CREATE TABLE IF NOT EXISTS participante (
    ci VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    email VARCHAR(50) NOT NULL
);


CREATE TABLE IF NOT EXISTS facultad (
    id_facultad VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);


CREATE TABLE IF NOT EXISTS programa_académico (
    nombre_programa VARCHAR(50) PRIMARY KEY,
    id_facultad VARCHAR(50) NOT NULL,
    tipo ENUM('grado','posgrado') NOT NULL,
    FOREIGN KEY (id_facultad) REFERENCES facultad(id_facultad)
);


-- Tabla participante_programa_académico corregida
CREATE TABLE IF NOT EXISTS participante_programa_académico (
    id_alumno_programa VARCHAR(50) PRIMARY KEY,
    ci_participante VARCHAR(20) NOT NULL,
    nombre_programa VARCHAR(50) NOT NULL,
    rol ENUM('alumno','docente') NOT NULL,
    FOREIGN KEY (ci_participante) REFERENCES participante(ci),
    FOREIGN KEY (nombre_programa) REFERENCES programa_académico(nombre_programa)
);


CREATE TABLE IF NOT EXISTS edificio (
    nombre_edificio VARCHAR(50) PRIMARY KEY,
    dirección VARCHAR(50) NOT NULL,
    departamento VARCHAR(50) NOT NULL
);


CREATE TABLE IF NOT EXISTS sala (
    nombre_sala VARCHAR(50) PRIMARY KEY,
    edificio VARCHAR(50) NOT NULL,
    capacidad INT NOT NULL,
    tipo_sala ENUM('libre','posgrado','docente') NOT NULL,
    FOREIGN KEY (edificio) REFERENCES edificio(nombre_edificio)
);


CREATE TABLE IF NOT EXISTS turno (
    id_turno VARCHAR(50) PRIMARY KEY,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL
);


CREATE TABLE IF NOT EXISTS reserva (
    id_reserva VARCHAR(50) PRIMARY KEY,
    nombre_sala VARCHAR(50) NOT NULL,
    edificio VARCHAR(50) NOT NULL,
    fecha DATE NOT NULL,
    id_turno VARCHAR(50) NOT NULL,
    estado ENUM('activa','cancelada','sin asistencia','finalizada') NOT NULL,
    FOREIGN KEY (nombre_sala) REFERENCES sala(nombre_sala),
    FOREIGN KEY (edificio) REFERENCES edificio(nombre_edificio),
    FOREIGN KEY (id_turno) REFERENCES turno(id_turno)
);


CREATE TABLE IF NOT EXISTS reserva_participante (
    ci_participante VARCHAR(20) NOT NULL,
    id_reserva VARCHAR(50) NOT NULL,
    fecha_solicitud_reserva DATE NOT NULL,
    asistencia BOOLEAN NOT NULL,
    PRIMARY KEY (ci_participante, id_reserva),
    FOREIGN KEY (ci_participante) REFERENCES participante(ci),
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva)
);


CREATE TABLE IF NOT EXISTS sancion_participante (
    ci_participante VARCHAR(20) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    PRIMARY KEY (ci_participante, fecha_inicio),
    FOREIGN KEY (ci_participante) REFERENCES participante(ci)
);

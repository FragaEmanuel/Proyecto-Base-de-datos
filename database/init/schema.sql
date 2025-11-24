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

CREATE TABLE IF NOT EXISTS programa_academico (
    nombre_programa VARCHAR(50) PRIMARY KEY,
    id_facultad VARCHAR(50) NOT NULL,
    tipo ENUM('grado','posgrado') NOT NULL,
    FOREIGN KEY (id_facultad) REFERENCES facultad(id_facultad)
);

CREATE TABLE IF NOT EXISTS participante_programa_academico (
    id_alumno_programa INT AUTO_INCREMENT PRIMARY KEY,
    ci_participante VARCHAR(20) NOT NULL,
    nombre_programa VARCHAR(50) NOT NULL,
    rol ENUM('alumno','docente') NOT NULL,
    FOREIGN KEY (ci_participante) REFERENCES participante(ci),
    FOREIGN KEY (nombre_programa) REFERENCES programa_academico(nombre_programa)
);

CREATE TABLE IF NOT EXISTS edificio (
    nombre_edificio VARCHAR(50) PRIMARY KEY,
    direccion VARCHAR(50) NOT NULL,
    departamento VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS sala (
    nombre_sala VARCHAR(50) NOT NULL,
    edificio VARCHAR(50) NOT NULL,
    capacidad INT NOT NULL,
    tipo_sala ENUM('libre','posgrado','docente') NOT NULL,
    PRIMARY KEY (nombre_sala, edificio),
    FOREIGN KEY (edificio) REFERENCES edificio(nombre_edificio)
);

CREATE TABLE IF NOT EXISTS turno (
    id_turno INT AUTO_INCREMENT PRIMARY KEY,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL
);

CREATE TABLE IF NOT EXISTS reserva (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,
    nombre_sala VARCHAR(50) NOT NULL,
    edificio VARCHAR(50) NOT NULL,
    fecha DATE NOT NULL,
    id_turno INT NOT NULL,
    estado ENUM('activa','cancelada','sin asistencia','finalizada') NOT NULL DEFAULT 'activa',
    FOREIGN KEY (nombre_sala, edificio) REFERENCES sala(nombre_sala, edificio),
    FOREIGN KEY (id_turno) REFERENCES turno(id_turno)
);

CREATE TABLE IF NOT EXISTS reserva_participante (
    ci_participante VARCHAR(20) NOT NULL,
    id_reserva INT NOT NULL,
    fecha_solicitud_reserva DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    asistencia BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (id_reserva, ci_participante),
    FOREIGN KEY (ci_participante) REFERENCES participante(ci),
    FOREIGN KEY (id_reserva) REFERENCES reserva(id_reserva)
);

CREATE TABLE IF NOT EXISTS sancion_participante (
    id_sancion INT AUTO_INCREMENT PRIMARY KEY,
    ci_participante VARCHAR(20) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    FOREIGN KEY (ci_participante) REFERENCES participante(ci)
);
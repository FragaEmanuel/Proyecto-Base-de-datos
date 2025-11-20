USE obligatorio;

-- Datos de login
INSERT IGNORE INTO login (correo, contraseña) VALUES
('admin@ucu.edu.uy', 'admin123'),
('funcionario@ucu.edu.uy', 'func123');

-- Datos de facultades
INSERT IGNORE INTO facultad (id_facultad, nombre) VALUES
('FING', 'Facultad de Ingeniería'),
('FCS', 'Facultad de Ciencias de la Salud'),
('FDE', 'Facultad de Empresariales');

-- Datos de programas academicos
INSERT IGNORE INTO programa_academico (nombre_programa, id_facultad, tipo) VALUES
('Ingeniería en Computación', 'FING', 'grado'),
('Licenciatura en Sistemas', 'FING', 'grado'),
('Maestría en Data Science', 'FING', 'posgrado'),
('Medicina', 'FCS', 'grado'),
('MBA', 'FDE', 'posgrado');

-- Datos de participantes
INSERT IGNORE INTO participante (ci, nombre, apellido, email) VALUES
('12345678', 'Juan', 'Pérez', 'juan.perez@ucu.edu.uy'),
('87654321', 'María', 'Gómez', 'maria.gomez@ucu.edu.uy'),
('11223344', 'Carlos', 'López', 'carlos.lopez@ucu.edu.uy'),
('44332211', 'Ana', 'Martínez', 'ana.martinez@ucu.edu.uy');

-- Datos de participantes en programas
INSERT IGNORE INTO participante_programa_academico (id_alumno_programa, ci_participante, nombre_programa, rol) VALUES
('AP001', '12345678', 'Ingeniería en Computación', 'alumno'),
('AP002', '87654321', 'Licenciatura en Sistemas', 'alumno'),
('AP003', '11223344', 'Maestría en Data Science', 'docente'),
('AP004', '44332211', 'Medicina', 'alumno');

-- Datos de edificios
INSERT IGNORE INTO edificio (nombre_edificio, direccion, departamento) VALUES
('Edificio Central', 'Av. 8 de Octubre 2738', 'Montevideo'),
('Edificio Norte', 'Av. Italia 6201', 'Montevideo'),
('Edificio Postgrado', 'Cnu. Gral. Flores 2456', 'Montevideo');

-- Datos de salas
INSERT IGNORE INTO sala (nombre_sala, edificio, capacidad, tipo_sala) VALUES
('Sala A1', 'Edificio Central', 10, 'libre'),
('Sala A2', 'Edificio Central', 8, 'libre'),
('Sala Posgrado 1', 'Edificio Postgrado', 6, 'posgrado'),
('Sala Docentes 1', 'Edificio Central', 4, 'docente');

-- Datos de turnos
INSERT IGNORE INTO turno (id_turno, hora_inicio, hora_fin) VALUES
('T08', '08:00:00', '09:00:00'),
('T09', '09:00:00', '10:00:00'),
('T10', '10:00:00', '11:00:00'),
('T11', '11:00:00', '12:00:00'),
('T14', '14:00:00', '15:00:00'),
('T15', '15:00:00', '16:00:00'),
('T16', '16:00:00', '17:00:00'),
('T17', '17:00:00', '18:00:00');
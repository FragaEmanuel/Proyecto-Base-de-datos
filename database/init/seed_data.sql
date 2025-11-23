USE obligatorio;

INSERT IGNORE INTO login (correo, contraseña) VALUES
('admin@ucu.edu.uy', 'admin123'),
('funcionario@ucu.edu.uy', 'func123');

INSERT IGNORE INTO facultad (id_facultad, nombre) VALUES
('FING', 'Facultad de Ingeniería'),
('FCS', 'Facultad de Ciencias de la Salud'),
('FDE', 'Facultad de Empresariales');

INSERT IGNORE INTO programa_academico (nombre_programa, id_facultad, tipo) VALUES
('Ingeniería en Computación', 'FING', 'grado'),
('Licenciatura en Sistemas', 'FING', 'grado'),
('Maestría en Data Science', 'FING', 'posgrado'),
('Medicina', 'FCS', 'grado'),
('MBA', 'FDE', 'posgrado');

INSERT IGNORE INTO participante (ci, nombre, apellido, email) VALUES
('12345678', 'Juan', 'Pérez', 'juan.perez@ucu.edu.uy'),
('87654321', 'María', 'Gómez', 'maria.gomez@ucu.edu.uy'),
('11223344', 'Carlos', 'López', 'carlos.lopez@ucu.edu.uy'),
('44332211', 'Ana', 'Martínez', 'ana.martinez@ucu.edu.uy'),
('55667788', 'Pablo', 'Silva', 'pablo.silva@ucu.edu.uy'),
('99887766', 'Lucía', 'Fernández', 'lucia.fernandez@ucu.edu.uy');

INSERT IGNORE INTO participante_programa_academico (ci_participante, nombre_programa, rol) VALUES
('12345678', 'Ingeniería en Computación', 'alumno'),
('87654321', 'Licenciatura en Sistemas', 'alumno'),
('44332211', 'Medicina', 'alumno'),
('55667788', 'Maestría en Data Science', 'alumno'),
('99887766', 'MBA', 'alumno'),
('11223344', 'Ingeniería en Computación', 'docente'),
('99887766', 'Maestría en Data Science', 'docente');

INSERT IGNORE INTO edificio (nombre_edificio, direccion, departamento) VALUES
('Edificio Central', 'Av. 8 de Octubre 2738', 'Montevideo'),
('Edificio Norte', 'Av. Italia 6201', 'Montevideo'),
('Edificio Postgrado', 'Cno. Gral. Flores 2456', 'Montevideo');

INSERT IGNORE INTO sala (nombre_sala, edificio, capacidad, tipo_sala) VALUES
('Sala A1', 'Edificio Central', 10, 'libre'),
('Sala A2', 'Edificio Central', 8, 'libre'),
('Sala B1', 'Edificio Norte', 5, 'libre'),
('Sala Posgrado 1', 'Edificio Postgrado', 6, 'posgrado'),
('Sala Docentes 1', 'Edificio Central', 4, 'docente');

INSERT IGNORE INTO turno (hora_inicio, hora_fin) VALUES
('08:00:00', '09:00:00'),
('09:00:00', '10:00:00'),
('10:00:00', '11:00:00'),
('11:00:00', '12:00:00'),
('14:00:00', '15:00:00'),
('15:00:00', '16:00:00'),
('16:00:00', '17:00:00'),
('17:00:00', '18:00:00');

INSERT IGNORE INTO sancion_participante (ci_participante, fecha_inicio, fecha_fin) VALUES
('44332211', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 2 MONTH));

INSERT IGNORE INTO reserva (nombre_sala, edificio, fecha, id_turno, estado) VALUES
('Sala A1', 'Edificio Central', '2025-11-20', 1, 'activa'),
('Sala A1', 'Edificio Central', '2025-11-20', 2, 'finalizada'),
('Sala A2', 'Edificio Central', '2025-11-20', 1, 'cancelada'),
('Sala Posgrado 1', 'Edificio Postgrado', '2025-11-20', 3, 'sin asistencia'),
('Sala Docentes 1', 'Edificio Central', '2025-11-21', 4, 'activa');

INSERT IGNORE INTO reserva_participante (id_reserva, ci_participante, asistencia) VALUES
(1, '12345678', 1),
(1, '87654321', 1),
(2, '12345678', 0),
(2, '11223344', 1),
(3, '87654321', 0),
(4, '55667788', 0),
(5, '11223344', 1);

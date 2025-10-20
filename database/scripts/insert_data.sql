-- database/seeds/sample_data.sql
INSERT INTO users (username, email) VALUES 
('usuario1', 'user1@example.com'),
('usuario2', 'user2@example.com');

INSERT INTO posts (user_id, title, content) VALUES
(1, 'Mi primer post', 'Contenido de ejemplo...');
CREATE TABLE Video(
    usuario_id INT(11),
    tamanyo FLOAT(11),
    ruta_aws VARCHAR(500) UNIQUE,
    id INT(11) PRIMARY KEY,
    fecha_subida DATETIME
)

CREATE TABLE Voto(
    usuario_id INT(11),
    video_id INT(11),
    valor INT(1),
    id INT(11) PRIMARY KEY,
    UNIQUE(usuario_id,video_id)
)

CREATE TABLE Comentario(
    id INT(11) PRIMARY KEY,
    usuario_id INT(11),
    video_id INT(11),
    contenido VARCHAR(255),
    comentario_padre_id INT(11) FOREIGN KEY REFERENCES Comentario(id)
)

CREATE TABLE Usuario (
  id INT(11) NOT NULL,
  nombre_completo varchar(100) NOT NULL,
  email varchar(100) NOT NULL,
  nombre_usuario varchar(30) NOT NULL,
  contraseÃ±a varchar(255) NOT NULL,
  frase_recuperacion varchar(100) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY usuario_UN1(email),
  UNIQUE KEY usuario_UN2 (nombre_usuario),
)

CREATE TABLE Video_Tags (
  video_id INT(11) NOT NULL,
  tag varchar(30) NOT NULL,
)

ALTER TABLE Video ADD CONSTRAINT FK_Video_Usuario FOREIGN KEY usuario_id REFERENCES Usuario(id);
ALTER TABLE Voto ADD CONSTRAINT FK_Voto_Usuario FOREIGN KEY usuario_id REFERENCES Usuario(id);
ALTER TABLE Voto ADD CONSTRAINT FK_Voto_Video FOREIGN KEY video_id REFERENCES Video(id);
ALTER TABLE Comentario ADD CONSTRAINT FK_Comentario_Video FOREIGN KEY video_id REFERENCES Video(id);
ALTER TABLE Comentario ADD CONSTRAINT FK_Comentario_Usuario FOREIGN KEY usuario_id REFERENCES Usuario(id);
ALTER TABLE Video_Tags ADD CONSTRAINT FK_Video_Tags_Video FOREIGN KEY video_id REFERENCES Video(id);

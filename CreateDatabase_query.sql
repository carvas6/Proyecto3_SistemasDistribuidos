CREATE TABLE Video(
    usuarioId INT(11),
    tamanyo FLOAT(11),
    rutaAWS VARCHAR(500) UNIQUE,
    id INT(11) PRIMARY KEY,
    fechaSubida DATETIME
) ENGINE = INNODB;

CREATE TABLE Voto(
    usuarioId INT(11),
    videoId INT(11),
    valor INT(1),
    id INT(11) PRIMARY KEY,
    UNIQUE(usuarioId,videoId)
) ENGINE = INNODB;

CREATE TABLE Comentario(
    id INT(11) PRIMARY KEY,
    usuarioId INT(11),
    videoId INT(11),
    contenido VARCHAR(255),
    comentarioPadreId INT(11),
    FOREIGN KEY(comentarioPadreId) REFERENCES Comentario(id)
) ENGINE = INNODB;

CREATE TABLE Usuario (
  id INT(11) NOT NULL,
  nombreCompleto varchar(100) NOT NULL,
  email varchar(100) NOT NULL,
  nombreUsuario varchar(30) NOT NULL,
  contrasenya varchar(255) NOT NULL,
  fraseRecuperacion varchar(100) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY usuario_UN1(email),
  UNIQUE KEY usuario_UN2 (nombreUsuario)
) ENGINE = INNODB;

CREATE TABLE Video_Tags (
  videoId INT(11) NOT NULL,
  tag varchar(30) NOT NULL
) ENGINE = INNODB;

ALTER TABLE Video ADD CONSTRAINT FK_Video_Usuario FOREIGN KEY(usuarioId) REFERENCES Usuario(id);
ALTER TABLE Voto ADD CONSTRAINT FK_Voto_Usuario FOREIGN KEY(usuarioId) REFERENCES Usuario(id);
ALTER TABLE Voto ADD CONSTRAINT FK_Voto_Video FOREIGN KEY(videoId) REFERENCES Video(id);
ALTER TABLE Comentario ADD CONSTRAINT FK_Comentario_Video FOREIGN KEY(videoId) REFERENCES Video(id);
ALTER TABLE Comentario ADD CONSTRAINT FK_Comentario_Usuario FOREIGN KEY(usuarioId) REFERENCES Usuario(id);
ALTER TABLE Video_Tags ADD CONSTRAINT FK_Video_Tags_Video FOREIGN KEY(videoId) REFERENCES Video(id);

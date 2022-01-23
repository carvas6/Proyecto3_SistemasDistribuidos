CREATE TABLE Video(
    usuarioId INT(11) NOT NULL,
    rutaAWS VARCHAR(500) UNIQUE NOT NULL,
    rutaAWSMiniatura VARCHAR(500),
    id INT(11) PRIMARY KEY AUTO_INCREMENT,
    fechaSubida DateTime DEFAULT NOW(),
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(500),
    ultimaModificacion DateTime DEFAULT NOW()
) ENGINE = INNODB;

CREATE TABLE Voto(
    usuarioId INT(11) NOT NULL,
    videoId INT(11) NOT NULL,
    valor INT(1) NOT NULL,
    id INT(11) PRIMARY KEY AUTO_INCREMENT,
    UNIQUE(usuarioId,videoId)
) ENGINE = INNODB;

CREATE TABLE Comentario(
    id INT(11) PRIMARY KEY AUTO_INCREMENT,
    usuarioId INT(11) NOT NULL,
    videoId INT(11) NOT NULL,
    contenido VARCHAR(255) NOT NULL,
    comentarioPadreId INT(11),
    FOREIGN KEY(comentarioPadreId) REFERENCES Comentario(id)
) ENGINE = INNODB;

CREATE TABLE Usuario (
  id INT(11) NOT NULL AUTO_INCREMENT,
  nombreCompleto varchar(100) NOT NULL,
  email varchar(100) NOT NULL,
  nombreUsuario varchar(30) NOT NULL,
  contrasenya varchar(255) NOT NULL,
  fraseRecuperacion varchar(100) NOT NULL,
  habilidado BOOLEAN DEFAULT TRUE,
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

-- =====================================================================
-- Práctica N° 4 - Tablón de Anuncios
-- Base de datos: bd_anuncios (MariaDB / MySQL)
-- Motor: InnoDB, codificación utf8mb4
-- =====================================================================

CREATE DATABASE IF NOT EXISTS bd_anuncios
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE bd_anuncios;

-- ---------------------------------------------------------------------
-- Tabla: usuarios
-- Personas que publican anuncios y administran el sistema.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario    INT           NOT NULL AUTO_INCREMENT,
    nombre        VARCHAR(120)  NOT NULL,
    username      VARCHAR(50)   NOT NULL,
    email         VARCHAR(150)  NOT NULL,
    password_hash VARCHAR(255)  NOT NULL,
    rol           VARCHAR(20)   NOT NULL DEFAULT 'usuario',
    activo        TINYINT(1)    NOT NULL DEFAULT 1,
    creado_en     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id_usuario),
    UNIQUE KEY uq_usuarios_username (username),
    UNIQUE KEY uq_usuarios_email (email),
    KEY ix_usuarios_rol (rol),
    CONSTRAINT ck_usuarios_rol CHECK (rol IN ('admin', 'usuario'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Tabla: categorias
-- Clasificación temática de los anuncios.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INT          NOT NULL AUTO_INCREMENT,
    nombre       VARCHAR(80)  NOT NULL,
    descripcion  VARCHAR(255) NULL,
    creado_en    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id_categoria),
    UNIQUE KEY uq_categorias_nombre (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------
-- Tabla: anuncios
-- Publicaciones del tablón. Cada anuncio pertenece a un usuario
-- (autor) y a una categoría.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS anuncios (
    id_anuncio        INT          NOT NULL AUTO_INCREMENT,
    titulo            VARCHAR(150) NOT NULL,
    contenido         TEXT         NOT NULL,
    fecha_publicacion DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actualizado_en    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                   ON UPDATE CURRENT_TIMESTAMP,
    id_usuario        INT          NOT NULL,
    id_categoria      INT          NOT NULL,

    PRIMARY KEY (id_anuncio),
    KEY ix_anuncios_titulo (titulo),
    KEY ix_anuncios_usuario (id_usuario),
    KEY ix_anuncios_categoria (id_categoria),
    KEY ix_anuncios_fecha (fecha_publicacion),

    -- Al eliminar un usuario se eliminan sus anuncios (1:N, CASCADE).
    CONSTRAINT fk_anuncios_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
        ON DELETE CASCADE ON UPDATE CASCADE,

    -- No se puede eliminar una categoría que tenga anuncios (1:N, RESTRICT).
    CONSTRAINT fk_anuncios_categoria
        FOREIGN KEY (id_categoria) REFERENCES categorias (id_categoria)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

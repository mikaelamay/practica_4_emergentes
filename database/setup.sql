-- Ejecutar como usuario root de MariaDB/MySQL:
--   mysql -u root -p < database/setup.sql
--
-- Crea el usuario de la aplicación y le otorga permisos sobre bd_anuncios.

CREATE DATABASE IF NOT EXISTS bd_anuncios
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'anuncios_user'@'localhost'
  IDENTIFIED BY 'anuncios_pass';

CREATE USER IF NOT EXISTS 'anuncios_user'@'127.0.0.1'
  IDENTIFIED BY 'anuncios_pass';

GRANT ALL PRIVILEGES ON bd_anuncios.* TO 'anuncios_user'@'localhost';
GRANT ALL PRIVILEGES ON bd_anuncios.* TO 'anuncios_user'@'127.0.0.1';

FLUSH PRIVILEGES;

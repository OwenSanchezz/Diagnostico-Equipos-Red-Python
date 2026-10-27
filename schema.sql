-- Diagnóstico de equipos y red
-- Autor: Owen Yamil Campuzano Sanchez (OwenSanchezz)

CREATE DATABASE IF NOT EXISTS diagnosticos_red
  CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE diagnosticos_red;

CREATE TABLE IF NOT EXISTS equipos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  hostname VARCHAR(100) NOT NULL UNIQUE,
  sistema VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS diagnosticos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  equipo_id INT NOT NULL,
  fecha DATETIME NOT NULL,
  cpu_porcentaje DECIMAL(5,1) NOT NULL,
  ram_porcentaje DECIMAL(5,1) NOT NULL,
  disco_porcentaje DECIMAL(5,1) NOT NULL,
  alertas VARCHAR(255) NOT NULL DEFAULT '',
  FOREIGN KEY (equipo_id) REFERENCES equipos(id)
);

CREATE TABLE IF NOT EXISTS pruebas_host (
  id INT AUTO_INCREMENT PRIMARY KEY,
  diagnostico_id INT NOT NULL,
  host VARCHAR(255) NOT NULL,
  ping BOOLEAN NOT NULL,
  FOREIGN KEY (diagnostico_id) REFERENCES diagnosticos(id)
);

CREATE TABLE IF NOT EXISTS pruebas_puerto (
  id INT AUTO_INCREMENT PRIMARY KEY,
  prueba_host_id INT NOT NULL,
  puerto INT NOT NULL,
  abierto BOOLEAN NOT NULL,
  FOREIGN KEY (prueba_host_id) REFERENCES pruebas_host(id)
);

# Diagnóstico de equipos y red

Sistema en Python que revisa el estado de un equipo de cómputo (CPU, RAM y disco) y de la red (ping y puertos de otros dispositivos), guarda cada diagnóstico en MySQL y lo expone con una API en Flask.

Lo armé a partir de lo que hacía en mi trabajo como técnico de TI: diagnóstico de equipos y revisión de conexiones de red.

**Autor:** Owen Yamil Campuzano Sanchez ([OwenSanchezz](https://github.com/OwenSanchezz))

## Qué hace

- Lee el uso de CPU, RAM y disco del equipo y marca alertas si alguno pasa del 90%.
- Hace ping y prueba puertos TCP en los dispositivos que se le indiquen (router, cámaras, servidores, etc.).
- Guarda cada diagnóstico en una base de datos MySQL con historial.
- Permite consultar el historial y lanzar diagnósticos nuevos por medio de una API.

## Tecnologías

Python, psutil, MySQL, mysql-connector-python y Flask.

## Estructura

| Archivo | Qué hace |
|---|---|
| `diagnostico.py` | Funciones de diagnóstico del equipo y la red |
| `schema.sql` | Crea la base `diagnosticos_red` (4 tablas en 3FN) |
| `db.py` | Conexión a MySQL y guardado de diagnósticos |
| `main.py` | Corre un diagnóstico y lo guarda |
| `api.py` | API REST con Flask |

## Base de datos

Cuatro tablas relacionadas con llaves foráneas: `equipos`, `diagnosticos`, `pruebas_host` y `pruebas_puerto`.

## Instalación

1. Clona el repositorio y entra a la carpeta.
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Crea la base de datos ejecutando `schema.sql` en MySQL (por ejemplo desde MySQL Workbench).
4. Crea un usuario para el proyecto:
   ```sql
   CREATE USER 'diagnostico'@'localhost' IDENTIFIED BY 'tu_contraseña';
   GRANT ALL PRIVILEGES ON diagnosticos_red.* TO 'diagnostico'@'localhost';
   ```

## Uso

La contraseña no está en el código. Se pide al ejecutar, o se puede definir con la variable `DB_PASSWORD`. El usuario por defecto es `root`; se cambia con `DB_USER`.

En PowerShell:

```
$env:DB_USER="diagnostico"
python main.py
```

Esto corre un diagnóstico y lo guarda. Los hosts y puertos a revisar se editan en la lista `DESTINOS` de `main.py`.

### API

```
python api.py
```

Corre en `http://127.0.0.1:5000` (solo accesible desde el propio equipo).

| Ruta | Descripción |
|---|---|
| `GET /equipos` | Lista los equipos registrados |
| `GET /equipos/<id>/diagnosticos?limite=10` | Historial de un equipo |
| `GET /diagnosticos/<id>` | Detalle de un diagnóstico con sus pruebas de red |
| `POST /diagnosticos` | Corre un diagnóstico nuevo y lo guarda |

Ejemplo en PowerShell:

```
Invoke-RestMethod -Method Post http://127.0.0.1:5000/diagnosticos
```

## Ideas para seguir

- Autenticación en la API.
- Diagnósticos programados cada cierto tiempo.
- Revisar varios equipos de la red, no solo el local.

"""
Guardado de diagnósticos en MySQL
Autor: Owen Yamil Campuzano Sanchez (OwenSanchezz)
"""
import os
from getpass import getpass

import mysql.connector

CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "database": "diagnosticos_red",
}


def conectar():
    """Conecta a MySQL. La contraseña viene de DB_PASSWORD o se pide al correr."""
    password = os.getenv("DB_PASSWORD")
    if password is None:
        password = getpass(f"Contraseña MySQL de {CONFIG['user']} (Enter si no tiene): ")
    return mysql.connector.connect(password=password, **CONFIG)


def guardar_diagnostico(conn, d):
    """Guarda un diagnóstico completo (el dict que devuelve diagnosticar())."""
    cur = conn.cursor()
    try:
        e = d["equipo"]

        # 1) equipo: lo crea si no existe, si existe actualiza el sistema
        cur.execute(
            "INSERT INTO equipos (hostname, sistema) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE sistema = VALUES(sistema), id = LAST_INSERT_ID(id)",
            (e["hostname"], e["sistema"]),
        )
        equipo_id = cur.lastrowid

        # 2) diagnóstico
        cur.execute(
            "INSERT INTO diagnosticos "
            "(equipo_id, fecha, cpu_porcentaje, ram_porcentaje, disco_porcentaje, alertas) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (equipo_id, d["fecha"].replace("T", " "), e["cpu_porcentaje"],
             e["ram_porcentaje"], e["disco_porcentaje"], ", ".join(d["alertas"])),
        )
        diag_id = cur.lastrowid

        # 3) pruebas de red: un registro por host y uno por puerto
        for r in d["red"]:
            cur.execute(
                "INSERT INTO pruebas_host (diagnostico_id, host, ping) VALUES (%s, %s, %s)",
                (diag_id, r["host"], r["ping"]),
            )
            host_id = cur.lastrowid
            for puerto, abierto in r["puertos"].items():
                cur.execute(
                    "INSERT INTO pruebas_puerto (prueba_host_id, puerto, abierto) "
                    "VALUES (%s, %s, %s)",
                    (host_id, int(puerto), abierto),
                )
        conn.commit()
        return diag_id
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()

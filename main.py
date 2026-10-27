"""
Corre el diagnóstico y lo guarda en MySQL
Autor: Owen Yamil Campuzano Sanchez (OwenSanchezz)
"""
from db import conectar, guardar_diagnostico
from diagnostico import diagnosticar

DESTINOS = [
    ("8.8.8.8", [53]),          # internet
    ("127.0.0.1", [80, 3306]),  # equipo local: web y MySQL
]

if __name__ == "__main__":
    resultado = diagnosticar(DESTINOS)
    conn = conectar()
    try:
        diag_id = guardar_diagnostico(conn, resultado)
        print(f"Diagnóstico guardado con id {diag_id}")
    finally:
        conn.close()

"""
API del sistema de diagnóstico de equipos y red
Autor: Owen Yamil Campuzano Sanchez (OwenSanchezz)
"""
import os
from getpass import getpass

from flask import Flask, jsonify, request

from db import conectar, guardar_diagnostico
from diagnostico import diagnosticar
from main import DESTINOS

app = Flask(__name__)
app.json.ensure_ascii = False


def consulta(sql, params=()):
    """Corre un SELECT y devuelve lista de dicts."""
    conn = conectar()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        filas = cur.fetchall()
        cur.close()
        return filas
    finally:
        conn.close()


def limpiar(fila):
    """Convierte Decimal y datetime a tipos que JSON entiende."""
    for k, v in fila.items():
        if hasattr(v, "isoformat"):
            fila[k] = v.isoformat(sep=" ")
        elif v.__class__.__name__ == "Decimal":
            fila[k] = float(v)
    return fila


@app.get("/")
def inicio():
    return jsonify({
        "api": "Diagnóstico de equipos y red",
        "rutas": [
            "GET /equipos",
            "GET /equipos/<id>/diagnosticos?limite=10",
            "GET /diagnosticos/<id>",
            "POST /diagnosticos",
        ],
    })


@app.get("/equipos")
def listar_equipos():
    return jsonify(consulta("SELECT id, hostname, sistema FROM equipos ORDER BY id"))


@app.get("/equipos/<int:equipo_id>/diagnosticos")
def historial(equipo_id):
    limite = min(request.args.get("limite", 10, type=int), 100)
    equipo = consulta("SELECT id FROM equipos WHERE id = %s", (equipo_id,))
    if not equipo:
        return jsonify({"error": "Equipo no encontrado"}), 404
    filas = consulta(
        "SELECT id, fecha, cpu_porcentaje, ram_porcentaje, disco_porcentaje, alertas "
        "FROM diagnosticos WHERE equipo_id = %s ORDER BY fecha DESC, id DESC LIMIT %s",
        (equipo_id, limite),
    )
    return jsonify([limpiar(f) for f in filas])


@app.get("/diagnosticos/<int:diag_id>")
def detalle(diag_id):
    diag = consulta(
        "SELECT d.id, d.fecha, d.cpu_porcentaje, d.ram_porcentaje, d.disco_porcentaje, "
        "d.alertas, e.hostname, e.sistema "
        "FROM diagnosticos d JOIN equipos e ON e.id = d.equipo_id WHERE d.id = %s",
        (diag_id,),
    )
    if not diag:
        return jsonify({"error": "Diagnóstico no encontrado"}), 404
    resultado = limpiar(diag[0])
    pruebas = consulta(
        "SELECT h.host, h.ping, p.puerto, p.abierto "
        "FROM pruebas_host h LEFT JOIN pruebas_puerto p ON p.prueba_host_id = h.id "
        "WHERE h.diagnostico_id = %s ORDER BY h.id, p.puerto",
        (diag_id,),
    )
    red = {}
    for f in pruebas:
        h = red.setdefault(f["host"], {"host": f["host"], "ping": bool(f["ping"]), "puertos": {}})
        if f["puerto"] is not None:
            h["puertos"][str(f["puerto"])] = bool(f["abierto"])
    resultado["red"] = list(red.values())
    return jsonify(resultado)


@app.post("/diagnosticos")
def nuevo_diagnostico():
    """Corre un diagnóstico ahora mismo y lo guarda."""
    resultado = diagnosticar(DESTINOS)
    conn = conectar()
    try:
        resultado["id"] = guardar_diagnostico(conn, resultado)
    finally:
        conn.close()
    return jsonify(resultado), 201


if __name__ == "__main__":
    if os.getenv("DB_PASSWORD") is None:
        os.environ["DB_PASSWORD"] = getpass("Contraseña MySQL (Enter si no tiene): ")
    app.run(host="127.0.0.1", port=5000)

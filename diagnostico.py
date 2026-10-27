"""
Diagnóstico de equipos y red
Autor: Owen Yamil Campuzano Sanchez (OwenSanchezz)
"""
import json
import platform
import socket
import subprocess
from datetime import datetime

import psutil


def info_equipo():
    """Estado general del equipo local."""
    disco = psutil.disk_usage("/")
    return {
        "hostname": socket.gethostname(),
        "sistema": f"{platform.system()} {platform.release()}",
        "cpu_porcentaje": psutil.cpu_percent(interval=1),
        "ram_porcentaje": psutil.virtual_memory().percent,
        "disco_porcentaje": disco.percent,
    }


def hacer_ping(host, intentos=3):
    """True si el host responde al ping."""
    flag = "-n" if platform.system() == "Windows" else "-c"
    try:
        resultado = subprocess.run(
            ["ping", flag, str(intentos), host],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return resultado.returncode == 0


def puerto_abierto(host, puerto, timeout=2):
    """True si el puerto TCP acepta conexión."""
    try:
        with socket.create_connection((host, puerto), timeout=timeout):
            return True
    except OSError:
        return False


def clasificar(equipo):
    """Marca el equipo como ok o con alerta según su uso de recursos."""
    alertas = []
    if equipo["cpu_porcentaje"] > 90:
        alertas.append("CPU alta")
    if equipo["ram_porcentaje"] > 90:
        alertas.append("RAM alta")
    if equipo["disco_porcentaje"] > 90:
        alertas.append("Disco casi lleno")
    return alertas


def diagnosticar(destinos):
    """destinos: lista de (host, [puertos])"""
    equipo = info_equipo()
    red = []
    for host, puertos in destinos:
        red.append({
            "host": host,
            "ping": hacer_ping(host),
            "puertos": {p: puerto_abierto(host, p) for p in puertos},
        })
    return {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "equipo": equipo,
        "alertas": clasificar(equipo),
        "red": red,
    }


if __name__ == "__main__":
    destinos = [
        ("8.8.8.8", [53]),         # internet
        ("127.0.0.1", [80, 3306]),  # equipo local: web y MySQL
    ]
    print(json.dumps(diagnosticar(destinos), indent=2, ensure_ascii=False))

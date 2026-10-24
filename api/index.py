from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from datetime import datetime
import os

app = FastAPI(
    title="DockGuard BAS - Etapa 1 (Monitoreo Básico de Atraque)",
    description="API en Python conectada en vivo con el panel visual de atraque",
    version="1.1.0"
)

# =====================================================================
# 1. PARÁMETROS EDITABLES EN PYTHON (SE VEN DIRECTAMENTE EN LA APP FINAL)
# Edita cualquiera de estos valores en este archivo (api/index.py) y
# al guardar / subir a GitHub se actualizarán automáticamente en la web.
# =====================================================================
CONFIG_MUELLE = {
    "titulo_muelle": "Monitoreo de Atraque en Muelle",
    "velocidad_inicial_cms": 6.0,     # Velocidad con la que inicia el simulador (cm/s)
    "angulo_inicial_deg": 1.0,        # Ángulo con el que inicia el simulador (°)
    "distancia_inicial_m": 35.0,      # Distancia inicial del buque al muelle (m)
    "velocidad_max_cms": 10.0,        # Límite para activar ALERTA ROJA de velocidad (cm/s)
    "velocidad_precaucion_cms": 8.0,  # Límite para activar PRECAUCIÓN de velocidad (cm/s)
    "angulo_max_deg": 5.0,            # Límite para activar ALERTA ROJA de ángulo (± grados)
    "angulo_precaucion_deg": 3.5      # Límite para activar PRECAUCIÓN de ángulo (± grados)
}


class LecturaBasicaSensor(BaseModel):
    distancia_proa_m: float = Field(..., ge=0, example=24.5)
    distancia_popa_m: float = Field(..., ge=0, example=25.3)
    velocidad_proa_cms: float = Field(..., ge=0, example=6.3)
    velocidad_popa_cms: float = Field(..., ge=0, example=5.7)
    angulo_atraque_deg: float = Field(default=1.0, example=1.0)


@app.get("/", response_class=HTMLResponse)
def servir_panel_etapa1():
    """
    Lee la plantilla HTML y le inyecta dinámicamente los valores configurados
    en Python (CONFIG_MUELLE) para que cualquier cambio en Python se vea en la app.
    """
    ruta_html = os.path.join(os.path.dirname(__file__), "simulador.html")
    if not os.path.exists(ruta_html):
        return "<h1>Monitoreo de Atraque - Etapa 1 Activa</h1>"

    with open(ruta_html, "r", encoding="utf-8") as f:
        html = f.read()

    # Inyectar valores de Python en la interfaz web
    html = html.replace("Monitoreo de Atraque en Muelle", CONFIG_MUELLE["titulo_muelle"])
    html = html.replace("distanceM: 35.0,", f"distanceM: {CONFIG_MUELLE['distancia_inicial_m']},")
    html = html.replace("speedCms: 6.0,", f"speedCms: {CONFIG_MUELLE['velocidad_inicial_cms']},")
    html = html.replace("angleDeg: 1.0,", f"angleDeg: {CONFIG_MUELLE['angulo_inicial_deg']},")
    html = html.replace("maxSafeSpeedCms: 10.0,", f"maxSafeSpeedCms: {CONFIG_MUELLE['velocidad_max_cms']},")
    html = html.replace("warnSpeedCms: 8.0,", f"warnSpeedCms: {CONFIG_MUELLE['velocidad_precaucion_cms']},")
    html = html.replace("maxSafeAngleDeg: 5.0,", f"maxSafeAngleDeg: {CONFIG_MUELLE['angulo_max_deg']},")
    html = html.replace("warnAngleDeg: 3.5", f"warnAngleDeg: {CONFIG_MUELLE['angulo_precaucion_deg']}")

    return html


@app.get("/api/config")
def obtener_configuracion():
    """Devuelve en formato JSON la configuración actual definida en Python."""
    return CONFIG_MUELLE


@app.post("/api/telemetria")
def evaluar_atraque_basico(lectura: LecturaBasicaSensor):
    """Evalúa velocidad, distancia y ángulo según los umbrales definidos en CONFIG_MUELLE."""
    vel_max_cms = max(lectura.velocidad_proa_cms, lectura.velocidad_popa_cms)
    dist_promedio_m = (lectura.distancia_proa_m + lectura.distancia_popa_m) / 2.0

    exceso_velocidad = vel_max_cms > CONFIG_MUELLE["velocidad_max_cms"]
    exceso_angulo = abs(lectura.angulo_atraque_deg) > CONFIG_MUELLE["angulo_max_deg"]

    if exceso_velocidad and exceso_angulo:
        estado = "ALERTA_EXCESO_VELOCIDAD_Y_ANGULO"
    elif exceso_velocidad:
        estado = "ALERTA_EXCESO_VELOCIDAD"
    elif exceso_angulo:
        estado = "ALERTA_EXCESO_ANGULO"
    else:
        estado = "APROXIMACION_SEGURA"

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "distancia_promedio_m": round(dist_promedio_m, 2),
        "velocidad_max_cms": round(vel_max_cms, 2),
        "angulo_atraque_deg": round(lectura.angulo_atraque_deg, 2),
        "exceso_velocidad": exceso_velocidad,
        "exceso_angulo": exceso_angulo,
        "estado": estado,
        "limites_activos": CONFIG_MUELLE
    }

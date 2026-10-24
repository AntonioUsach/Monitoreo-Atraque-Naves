from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from datetime import datetime
import os

app = FastAPI(
    title="DockGuard BAS - Etapa 1 (Monitoreo Básico de Atraque)",
    description="API Serverless en Python para monitorear velocidad, distancia y ángulo de atraque en muelle",
    version="1.0.0"
)

class LecturaBasicaSensor(BaseModel):
    distancia_proa_m: float = Field(..., ge=0, example=24.5)
    distancia_popa_m: float = Field(..., ge=0, example=25.3)
    velocidad_proa_cms: float = Field(..., ge=0, example=6.3)
    velocidad_popa_cms: float = Field(..., ge=0, example=5.7)
    angulo_atraque_deg: float = Field(default=1.0, example=1.0)


@app.get("/", response_class=HTMLResponse)
def servir_panel_etapa1():
    """Sirve la visualización en planta de la Etapa 1."""
    ruta_html = os.path.join(os.path.dirname(__file__), "simulador.html")
    if os.path.exists(ruta_html):
        with open(ruta_html, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Monitoreo de Atraque - Etapa 1 Activa</h1>"


@app.post("/api/telemetria")
def evaluar_atraque_basico(lectura: LecturaBasicaSensor):
    """Evalúa velocidad, distancia y ángulo de atraque y emite alertas por exceso."""
    vel_max_cms = max(lectura.velocidad_proa_cms, lectura.velocidad_popa_cms)
    dist_promedio_m = (lectura.distancia_proa_m + lectura.distancia_popa_m) / 2.0

    exceso_velocidad = vel_max_cms > 10.0
    exceso_angulo = abs(lectura.angulo_atraque_deg) > 5.0

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
        "estado": estado
    }

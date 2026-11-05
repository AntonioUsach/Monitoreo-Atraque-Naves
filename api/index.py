from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import urllib.request
import json
import os

app = FastAPI(
    title="DockGuard BAS - Etapa 2 (Monitoreo + Supabase en Vivo)",
    description="API Serverless en Python conectada con Supabase para almacenar y modificar registros cada 1 segundo",
    version="2.0.0"
)

# =====================================================================
# CONFIGURACIÓN DEL MUELLE Y CREDENCIALES DE SUPABASE EN PYTHON
# Puedes definir SUPABASE_URL y SUPABASE_KEY en Vercel (Environment Variables)
# o escribirlas directamente aquí entre las comillas.
# =====================================================================
CONFIG_MUELLE = {
    "titulo_muelle": "Monitoreo de Atraque en Muelle",
    "velocidad_inicial_cms": 6.0,
    "angulo_inicial_deg": 1.0,
    "distancia_inicial_m": 35.0,
    "velocidad_max_cms": 10.0,
    "velocidad_precaucion_cms": 8.0,
    "angulo_max_deg": 5.0,
    "angulo_precaucion_deg": 3.5,
    "supabase_url": os.environ.get("SUPABASE_URL", ""),
    "supabase_anon_key": os.environ.get("SUPABASE_KEY", "")
}


class RegistroSegundoAtraque(BaseModel):
    simulacion_id: str = Field(..., example="SIM-101")
    segundo: int = Field(..., ge=1, example=1)
    velocidad_proa_cms: float = Field(..., ge=0, example=6.2)
    velocidad_popa_cms: float = Field(..., ge=0, example=5.8)
    angulo_proa_deg: float = Field(..., example=1.0)
    angulo_popa_deg: float = Field(..., example=-1.0)
    distancia_proa_m: float = Field(..., ge=0, example=34.5)
    distancia_popa_m: float = Field(..., ge=0, example=35.5)
    estado_atraque: str = Field(..., example="APROXIMACION_SEGURA")


class ActualizacionRegistro(BaseModel):
    velocidad_proa_cms: Optional[float] = None
    velocidad_popa_cms: Optional[float] = None
    angulo_proa_deg: Optional[float] = None
    angulo_popa_deg: Optional[float] = None
    distancia_proa_m: Optional[float] = None
    distancia_popa_m: Optional[float] = None
    estado_atraque: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
def servir_panel_etapa2():
    """Sirve el panel de la Etapa 2 inyectando los parámetros y credenciales de Supabase."""
    ruta_html = os.path.join(os.path.dirname(__file__), "simulador.html")
    if not os.path.exists(ruta_html):
        return "<h1>Monitoreo de Atraque - Etapa 2 Activa</h1>"

    with open(ruta_html, "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("Monitoreo de Atraque en Muelle", CONFIG_MUELLE["titulo_muelle"])
    html = html.replace("distanceM: 35.0,", f"distanceM: {CONFIG_MUELLE['distancia_inicial_m']},")
    html = html.replace("speedCms: 6.0,", f"speedCms: {CONFIG_MUELLE['velocidad_inicial_cms']},")
    html = html.replace("angleDeg: 1.0,", f"angleDeg: {CONFIG_MUELLE['angulo_inicial_deg']},")
    html = html.replace("maxSafeSpeedCms: 10.0,", f"maxSafeSpeedCms: {CONFIG_MUELLE['velocidad_max_cms']},")
    html = html.replace("warnSpeedCms: 8.0,", f"warnSpeedCms: {CONFIG_MUELLE['velocidad_precaucion_cms']},")
    html = html.replace("maxSafeAngleDeg: 5.0,", f"maxSafeAngleDeg: {CONFIG_MUELLE['angulo_max_deg']},")
    html = html.replace("warnAngleDeg: 3.5,", f"warnAngleDeg: {CONFIG_MUELLE['angulo_precaucion_deg']},")

    if CONFIG_MUELLE["supabase_url"] and CONFIG_MUELLE["supabase_anon_key"]:
        html = html.replace('supabaseUrl: "",', f'supabaseUrl: "{CONFIG_MUELLE["supabase_url"]}",')
        html = html.replace('supabaseKey: ""', f'supabaseKey: "{CONFIG_MUELLE["supabase_anon_key"]}"')

    return html


@app.get("/api/registros")
def listar_registros_supabase():
    """Consulta las últimas 50 filas almacenadas en Supabase."""
    sb_url = CONFIG_MUELLE["supabase_url"].rstrip("/")
    sb_key = CONFIG_MUELLE["supabase_anon_key"]
    if not sb_url or not sb_key:
        raise HTTPException(status_code=400, detail="Faltan SUPABASE_URL y SUPABASE_KEY")

    endpoint = f"{sb_url}/rest/v1/registros_atraque?select=*&order=id.desc&limit=50"
    req = urllib.request.Request(
        endpoint,
        method="GET",
        headers={"apikey": sb_key, "Authorization": f"Bearer {sb_key}"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


@app.post("/api/guardar_simulacion")
def guardar_simulacion_supabase(registros: List[RegistroSegundoAtraque]):
    """Guarda en lote todos los registros capturados cada 1 segundo en Supabase."""
    sb_url = CONFIG_MUELLE["supabase_url"].rstrip("/")
    sb_key = CONFIG_MUELLE["supabase_anon_key"]
    if not sb_url or not sb_key:
        raise HTTPException(status_code=400, detail="Faltan SUPABASE_URL y SUPABASE_KEY")

    endpoint = f"{sb_url}/rest/v1/registros_atraque"
    payload = json.dumps([r.dict() for r in registros]).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Prefer": "return=representation"
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


@app.patch("/api/registros/{registro_id}")
def modificar_registro_en_vivo(registro_id: int, cambios: ActualizacionRegistro):
    """Modifica en vivo un registro existente en la tabla registros_atraque de Supabase."""
    sb_url = CONFIG_MUELLE["supabase_url"].rstrip("/")
    sb_key = CONFIG_MUELLE["supabase_anon_key"]
    if not sb_url or not sb_key:
        raise HTTPException(status_code=400, detail="Faltan SUPABASE_URL y SUPABASE_KEY")

    datos_limpios = {k: v for k, v in cambios.dict().items() if v is not None}
    endpoint = f"{sb_url}/rest/v1/registros_atraque?id=eq.{registro_id}"
    payload = json.dumps(datos_limpios).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=payload,
        method="PATCH",
        headers={
            "Content-Type": "application/json",
            "apikey": sb_key,
            "Authorization": f"Bearer {sb_key}",
            "Prefer": "return=representation"
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

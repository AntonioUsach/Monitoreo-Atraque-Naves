# ⚓ DockGuard BAS — Monitoreo de Velocidad de Atraque en Muelle (Python + Vercel)

Proyecto en **Python (FastAPI)** listo para subir a **GitHub** y desplegar en **Vercel**. Incluye:
1. **Panel y Simulador en Tiempo Real** (`/`): Visualización en planta del muelle, losa de hormigón, compresión de defensas D1–D6, sensores láser de Proa y Popa, y curvas de velocidad vs. distancia.
2. **Endpoint Serverless de Telemetría** (`POST /api/telemetria`): Recibe lecturas de sensores de velocidad y posición por HTTP, calcula la energía cinética de impacto según criterios PIANC y emite alertas de sobrecarga para proteger las defensas y la losa.

## Estructura del Repositorio

- `api/index.py`: Aplicación principal en Python con FastAPI.
- `api/simulador.html`: Interfaz gráfica del panel y simulador.
- `vercel.json`: Configuración para que Vercel ejecute Python de forma *serverless*.
- `requirements.txt`: Librerías de Python requeridas.

## Cómo subirlo a GitHub y conectarlo con Vercel

1. Crea un repositorio nuevo en [GitHub](https://github.com/new).
2. Sube los archivos de esta carpeta a tu repositorio:
   ```bash
   git init
   git add .
   git commit -m "Primer commit: Simulador y API de atraque en Python"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git push -u origin main
   ```
3. Entra a [Vercel](https://vercel.com), haz clic en **Add New... > Project**, selecciona tu repositorio de GitHub y presiona **Deploy**.

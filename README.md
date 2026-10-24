Monitoreo de Velocidad de Atraque en Muelle

1. **Panel y Simulador en Tiempo Real** (`/`): Visualización en planta del muelle, losa de hormigón, compresión de defensas D1–D6, sensores láser de Proa y Popa, y curvas de velocidad vs. distancia.
2. **Endpoint Serverless de Telemetría** (`POST /api/telemetria`): Recibe lecturas de sensores de velocidad y posición por HTTP, calcula la energía cinética de impacto según criterios PIANC y emite alertas de sobrecarga para proteger las defensas y la losa.




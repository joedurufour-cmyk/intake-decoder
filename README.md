# INTAKE Decoder v2 — Backend

Backend standalone para INTAKE Decoder. Sin LLM, sin API externa. Solo persistencia SQLite + endpoints REST.

## Endpoints

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/` | Sirve el frontend HTML |
| GET | `/health` | Estado del servicio |
| GET | `/api/reports` | Listar reportes guardados |
| POST | `/api/reports` | Guardar reporte nuevo |
| GET | `/api/reports/<id>` | Traer reporte por ID |
| DELETE | `/api/reports/<id>` | Borrar reporte |

## Frontend

El frontend (`intake-offline.html`) procesa todo localmente en el navegador:
- Corrección de texto
- Clasificación de intención
- Extracción de entidades
- Catalogación de variables
- Generación de tareas priorizadas
- Detección de gaps

El backend solo guarda/lee los reportes generados.

## Deploy en Render

1. Crear nuevo Web Service en Render
2. Conectar repo `joedurufour-cmyk/intake-decoder`
3. Runtime: Python 3
4. Start command: `python main.py`
5. Deploy

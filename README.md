# Lucius Fox

Sistema de asistencia ejecutiva con múltiples agentes autónomos especializados en diferentes áreas, coordinados por Lucius Fox.

## Despliegue en Render

Este proyecto está configurado para ser desplegado en Render como un servicio web usando Docker.

### Configuración

- **Runtime**: Docker
- **Dockerfile Path**: ./Dockerfile
- **Docker Build Context**: .
- **Environment Variables**:
  - `ENVIRONMENT`: production
  - `LOG_LEVEL`: INFO
  - `GROQ_API_KEY`: (Requerido)
  - `SLACK_BOT_TOKEN`: (Requerido)
  - `GOOGLE_CALENDAR_ID`: primary
  - `SLACK_SIGNING_SECRET`: (Requerido)
  - `PORT`: 8000

### Archivos Secretos

- `google_credentials.json`: Montado en `/etc/secrets/google_credentials.json`
- `slack_config.json`: Montado en `/etc/secrets/slack_config.json`

## Desarrollo Local

Para ejecutar el proyecto localmente:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

## Documentación

Para más detalles sobre el despliegue, consultar la [documentación de deployment](docs/render_deployment.md).

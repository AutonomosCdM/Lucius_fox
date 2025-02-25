# Deployment a Render

Este documento describe el proceso de deployment de Lucius Fox a [Render](https://render.com/).

## Requisitos Previos

- Cuenta en Render
- API Key de Render
- Credenciales de Google (Calendar, Gmail)
- Token de Slack

## Métodos de Deployment

Existen dos métodos para desplegar la aplicación en Render:

1. **Usando la CLI de Render** (Recomendado)
2. **Usando la API de Render**

### Método 1: Usando la CLI de Render

La CLI de Render proporciona una forma más sencilla y directa de desplegar la aplicación. Este método es recomendado por su simplicidad y fiabilidad.

#### Instalación de la CLI de Render

La CLI de Render se puede instalar de varias formas:

**Con Homebrew (macOS):**
```bash
brew update
brew install render
```

**Descarga directa (Linux/macOS):**
```bash
# Para macOS
curl -L https://github.com/render-oss/cli/releases/latest/download/cli_latest_darwin_amd64.zip -o render.zip
unzip render.zip
chmod +x cli_v*
sudo mv cli_v* /usr/local/bin/render

# Para Linux
curl -L https://github.com/render-oss/cli/releases/latest/download/cli_latest_linux_amd64.zip -o render.zip
unzip render.zip
chmod +x cli_v*
sudo mv cli_v* /usr/local/bin/render
```

#### Autenticación

La CLI de Render puede autenticarse de dos formas:

1. **Interactiva (para uso manual):**
   ```bash
   render login
   ```
   Este comando abrirá tu navegador para autorizar la CLI.

2. **Con API Key (para automatización):**
   ```bash
   export RENDER_API_KEY=YOUR_RENDER_API_KEY
   ```

#### Despliegue con el Script Automatizado

Hemos creado un script que automatiza todo el proceso de despliegue usando la CLI de Render:

```bash
./scripts/render_cli_deploy.sh
```

Este script:

1. Instala la CLI de Render si no está instalada
2. Verifica la autenticación y configura el espacio de trabajo
3. Verifica si el servicio ya existe, y lo crea si es necesario
4. Despliega la aplicación
5. Espera a que el despliegue se complete y muestra el resultado

**Opciones del script:**

- **Modo dry-run**: Simula el despliegue sin realizar cambios reales
  ```bash
  ./scripts/render_cli_deploy.sh --dry-run
  ```

- **API key personalizada**: Proporciona tu propia API key como argumento
  ```bash
  ./scripts/render_cli_deploy.sh tu_api_key
  ```

**Notas importantes:**

- Si el token de Render ha expirado, el script iniciará automáticamente el proceso de login, abriendo una ventana del navegador para autenticarte.
- Después de completar el proceso de login, deberás volver a ejecutar el script.
- El script seleccionará automáticamente el primer espacio de trabajo disponible si no hay uno configurado.

#### Comandos Útiles de la CLI

Algunos comandos útiles de la CLI de Render:

```bash
# Listar todos los servicios
render services --output json --confirm

# Crear un despliegue para un servicio específico
render deploys create SERVICE_ID --output json --confirm --wait

# Ver los logs de un servicio
render logs SERVICE_ID

# Abrir una sesión SSH en un servicio
render ssh SERVICE_ID
```

### Método 2: Usando la API de Render

Este método utiliza la API de Render directamente para desplegar la aplicación. Es más complejo que usar la CLI, pero ofrece más control sobre el proceso de despliegue.

#### Scripts Disponibles

El proyecto incluye varios scripts para facilitar el despliegue usando la API de Render:

- `scripts/deploy_to_render.py`: Script principal que interactúa con la API de Render
- `scripts/deploy.sh`: Script que orquesta todo el proceso de despliegue
- `scripts/prepare_credentials.py`: Script para preparar las credenciales para el despliegue

#### Proceso de Despliegue con la API

El proceso de despliegue con la API es el siguiente:

1. Configurar las variables de entorno necesarias
2. Ejecutar los tests para verificar que todo funciona correctamente
3. Preparar las credenciales para el despliegue
4. Crear o actualizar el servicio en Render usando la API
5. Iniciar el despliegue y monitorear su progreso

Para más detalles sobre este método, consulta las secciones siguientes.

## Preparación para el Deployment (Común para ambos métodos)

### 1. Configuración de Credenciales

Las credenciales necesarias para el deployment se encuentran en el directorio `credentials/`. Estas incluyen:

- `calendar_credentials.json`: Credenciales para Google Calendar
- `gmail_credentials.json`: Credenciales para Gmail
- `slack_config.json`: Configuración de Slack

### 2. Variables de Entorno

Las siguientes variables de entorno son necesarias para el deployment:

```
RENDER_API_KEY=YOUR_RENDER_API_KEY
RENDER_OWNER_ID=YOUR_RENDER_OWNER_ID  # Reemplazar con tu ID de propietario en Render
GROQ_API_KEY=YOUR_GROQ_API_KEY
SLACK_BOT_TOKEN=YOUR_SLACK_BOT_TOKEN
SLACK_SIGNING_SECRET=YOUR_SLACK_SIGNING_SECRET
```

#### Obtener el ID de Propietario de Render

Para obtener tu ID de propietario en Render, puedes usar el siguiente comando:

```bash
curl --request GET \
     --url 'https://api.render.com/v1/owners' \
     --header 'Accept: application/json' \
     --header 'Authorization: Bearer YOUR_RENDER_API_KEY'
```

Esto devolverá una lista de propietarios a los que tienes acceso. Busca el ID del propietario que deseas usar para el deployment.

## Proceso de Deployment

### 1. Preparación de Archivos

El proyecto incluye los siguientes archivos para el deployment:

- `Dockerfile`: Configuración de Docker para el proyecto
- `.dockerignore`: Archivos a excluir del contexto de Docker
- `scripts/prepare_credentials.py`: Script para preparar las credenciales
- `scripts/deploy_to_render.py`: Script para desplegar a Render usando la API
- `scripts/deploy.sh`: Script para ejecutar todo el proceso de deployment

### 2. Ejecución del Deployment

Para desplegar la aplicación a Render, ejecuta el siguiente comando:

```bash
./scripts/deploy.sh
```

El script admite las siguientes opciones:

- `--dry-run`: Realiza una simulación del deployment sin efectuar cambios reales
  ```bash
  ./scripts/deploy.sh --dry-run
  ```

- `--skip-tests`: Omite la ejecución de los tests (útil cuando hay dependencias faltantes)
  ```bash
  ./scripts/deploy.sh --skip-tests
  ```

Las opciones se pueden combinar:
```bash
./scripts/deploy.sh --dry-run --skip-tests
```

Este script realizará las siguientes acciones:

1. Configurar las variables de entorno necesarias
2. Ejecutar los tests para verificar que todo funciona correctamente
3. Preparar las credenciales para el deployment
4. Desplegar la aplicación a Render usando la API (o simular el deployment en modo dry-run)

### 3. Verificación del Deployment

Una vez completado el deployment, la aplicación estará disponible en:

```
https://lucius-fox.onrender.com
```

## Monitoreo y Logs

Para monitorear la aplicación y ver los logs, puedes usar el dashboard de Render o la API:

```bash
# Obtener logs del servicio
curl --request GET \
     --url 'https://api.render.com/v1/services/{service_id}/logs' \
     --header 'Accept: application/json' \
     --header 'Authorization: Bearer {RENDER_API_KEY}'
```

## Rollback

Si es necesario hacer un rollback a una versión anterior, puedes usar el dashboard de Render o la API:

```bash
# Obtener lista de deploys
curl --request GET \
     --url 'https://api.render.com/v1/services/{service_id}/deploys' \
     --header 'Accept: application/json' \
     --header 'Authorization: Bearer {RENDER_API_KEY}'

# Hacer rollback a un deploy específico
curl --request POST \
     --url 'https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}/rollback' \
     --header 'Accept: application/json' \
     --header 'Authorization: Bearer {RENDER_API_KEY}'
```

## Troubleshooting

### Problemas Comunes

1. **Error de Credenciales**: Verifica que las credenciales en el directorio `credentials/` sean válidas.
2. **Error de Variables de Entorno**: Asegúrate de que todas las variables de entorno estén configuradas correctamente.
3. **Error de Deployment**: Revisa los logs en el dashboard de Render para identificar el problema.

### Contacto

Si encuentras algún problema durante el deployment, contacta al equipo de desarrollo.

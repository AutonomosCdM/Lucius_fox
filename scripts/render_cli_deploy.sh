#!/bin/bash
# Script para desplegar la aplicación en Render usando la CLI de Render

# Colores para la salida
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Iniciando despliegue con Render CLI...${NC}"

# Verificar si la CLI de Render está instalada
if ! command -v render &> /dev/null; then
    echo -e "${YELLOW}Instalando Render CLI...${NC}"
    
    # Detectar el sistema operativo
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew update
        brew install render || {
            echo -e "${RED}Error al instalar Render CLI con Homebrew.${NC}"
            echo -e "${YELLOW}Intentando instalación directa...${NC}"
            
            # Instalación directa para macOS
            curl -L https://github.com/render-oss/cli/releases/latest/download/cli_latest_darwin_amd64.zip -o render.zip
            unzip render.zip
            chmod +x cli_v*
            sudo mv cli_v* /usr/local/bin/render
        }
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -L https://github.com/render-oss/cli/releases/latest/download/cli_latest_linux_amd64.zip -o render.zip
        unzip render.zip
        chmod +x cli_v*
        sudo mv cli_v* /usr/local/bin/render
    else
        echo -e "${RED}Sistema operativo no soportado para la instalación automática.${NC}"
        echo "Por favor, instala la CLI de Render manualmente desde: https://render.com/docs/cli"
        exit 1
    fi
    
    echo -e "${GREEN}Render CLI instalado correctamente.${NC}"
fi

# Verificar si se proporcionó una API key como argumento
if [ -n "$1" ]; then
    export RENDER_API_KEY="$1"
else
    # Usar la API key del archivo .env si existe
    if [ -f .env ] && grep -q "RENDER_API_KEY" .env; then
        export RENDER_API_KEY=$(grep "RENDER_API_KEY" .env | cut -d '=' -f2)
    else
        echo -e "${YELLOW}No se encontró RENDER_API_KEY. Por favor, proporciona una API key como argumento.${NC}"
        echo -e "${YELLOW}Ejemplo: ./scripts/render_cli_deploy.sh tu_api_key${NC}"
        exit 1
    fi
fi

# Verificar si el token es válido y configurar el espacio de trabajo
echo -e "${YELLOW}Verificando autenticación y configurando espacio de trabajo...${NC}"

# Intentar listar espacios de trabajo para verificar el token
WORKSPACE_LIST_RESULT=$(render workspace list --output json --confirm 2>&1)
if [[ "$WORKSPACE_LIST_RESULT" == *"token is expired"* ]] || [[ "$WORKSPACE_LIST_RESULT" == *"unauthorized"* ]]; then
    echo -e "${YELLOW}El token de Render ha expirado o no es válido. Iniciando proceso de login...${NC}"
    echo -e "${YELLOW}Se abrirá una ventana del navegador para autenticarte en Render.${NC}"
    echo -e "${YELLOW}Después de autenticarte, vuelve a ejecutar este script.${NC}"
    
    # Iniciar el proceso de login
    render login
    
    # Salir del script para que el usuario pueda completar el proceso de login
    echo -e "${YELLOW}Por favor, completa el proceso de login en el navegador y luego vuelve a ejecutar este script.${NC}"
    exit 1
fi

# Verificar si hay un espacio de trabajo configurado
WORKSPACE_SET=$(echo "$WORKSPACE_LIST_RESULT" | grep -o '"active":true' || echo "")

if [ -z "$WORKSPACE_SET" ]; then
    echo -e "${YELLOW}No hay un espacio de trabajo activo configurado.${NC}"
    
    # Obtener la lista de espacios de trabajo
    WORKSPACES=$(echo "$WORKSPACE_LIST_RESULT")
    
    # Si hay espacios de trabajo disponibles, seleccionar el primero
    if [[ "$WORKSPACES" != "[]" && "$WORKSPACES" != "" ]]; then
        WORKSPACE_ID=$(echo "$WORKSPACES" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
        if [ -n "$WORKSPACE_ID" ]; then
            echo -e "${YELLOW}Configurando espacio de trabajo: ${WORKSPACE_ID}${NC}"
            render workspace set "$WORKSPACE_ID" --confirm
            echo -e "${GREEN}Espacio de trabajo configurado exitosamente.${NC}"
        else
            echo -e "${RED}No se pudo obtener el ID del espacio de trabajo.${NC}"
            echo -e "${YELLOW}Por favor, configura manualmente un espacio de trabajo:${NC}"
            echo -e "${YELLOW}  render workspace set${NC}"
            exit 1
        fi
    else
        echo -e "${RED}No se encontraron espacios de trabajo disponibles.${NC}"
        echo -e "${YELLOW}Por favor, crea un espacio de trabajo en Render y vuelve a ejecutar este script.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Espacio de trabajo ya configurado.${NC}"
fi

# Verificar si ya existe un servicio con el nombre "lucius-fox"
echo -e "${YELLOW}Verificando si el servicio ya existe...${NC}"
SERVICE_ID=$(render services --output json --confirm 2>/dev/null | grep -o '"id":"[^"]*","name":"lucius-fox"' | cut -d'"' -f4 || echo "")

if [ -z "$SERVICE_ID" ]; then
    echo -e "${YELLOW}Creando nuevo servicio...${NC}"
    
    # Verificar si estamos en modo dry-run
    if [[ "$*" == *"--dry-run"* ]]; then
        echo -e "${YELLOW}Modo dry-run: Simulando creación de servicio...${NC}"
        echo -e "${GREEN}Servicio simulado creado exitosamente.${NC}"
        exit 0
    fi
    
    # Crear el servicio directamente con la CLI
    echo -e "${YELLOW}Creando servicio web con Docker...${NC}"
    render service create web \
        --name lucius-fox \
        --runtime docker \
        --repo https://github.com/AutonomosCdM/Lucius_fox.git \
        --branch main \
        --dockerfile ./Dockerfile \
        --env ENVIRONMENT=production \
        --env LOG_LEVEL=INFO \
        --env GROQ_API_KEY=YOUR_GROQ_API_KEY \
        --env SLACK_BOT_TOKEN=YOUR_SLACK_BOT_TOKEN \
        --env GOOGLE_CALENDAR_ID=primary \
        --env SLACK_SIGNING_SECRET=YOUR_SLACK_SIGNING_SECRET \
        --env PORT=8000 \
        --confirm
    
    # Obtener el ID del servicio recién creado
    SERVICE_ID=$(render services --output json --confirm | grep -o '"id":"[^"]*","name":"lucius-fox"' | cut -d'"' -f4)
    
    if [ -z "$SERVICE_ID" ]; then
        echo -e "${RED}Error: No se pudo crear el servicio.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Servicio creado con ID: ${SERVICE_ID}${NC}"
else
    echo -e "${GREEN}Servicio encontrado con ID: ${SERVICE_ID}${NC}"
fi

# Desplegar el servicio
echo -e "${YELLOW}Iniciando despliegue...${NC}"

# Verificar si estamos en modo dry-run
if [[ "$*" == *"--dry-run"* ]]; then
    echo -e "${YELLOW}Modo dry-run: Simulando despliegue...${NC}"
    echo -e "${GREEN}Despliegue simulado completado exitosamente.${NC}"
else
    render deploys create $SERVICE_ID --output json --confirm --wait
    echo -e "${GREEN}Despliegue completado exitosamente.${NC}"
    echo -e "${GREEN}La aplicación está disponible en: https://lucius-fox.onrender.com${NC}"
fi

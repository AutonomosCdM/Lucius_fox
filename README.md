# Sistema Autónomo Lucius Fox

![CI](https://github.com/AutonomosCdM/Lucius_fox/actions/workflows/main.yml/badge.svg)

## Descripción
Sistema de asistencia ejecutiva con múltiples agentes autónomos especializados en diferentes áreas, coordinados por Lucius Fox.

## Requisitos
- Python 3.10+
- Cuenta de Google para integración con Calendar y Gmail

## Instalación
1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/lucius_fox.git
cd lucius_fox
```

2. Crear entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate    # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Configuración
1. Crear archivo `.env` en la raíz del proyecto:
```bash
GOOGLE_CALENDAR_ID=primary
LOG_LEVEL=INFO
```

2. Configurar credenciales de Google (siguiendo las instrucciones en [docs/google_setup.md](docs/google_setup.md))

## Uso
Ejecutar el sistema principal:
```bash
python -m lucius_fox
```

### Deployment
Para desplegar el sistema en Render, tienes dos opciones:

#### Opción 1: Usando la CLI de Render (Recomendado)
```bash
./scripts/render_cli_deploy.sh
```

#### Opción 2: Usando la API de Render
```bash
./scripts/deploy.sh
```

Para más detalles sobre el deployment, consultar la [documentación de deployment](docs/render_deployment.md).

## Agentes Disponibles
- **Lucius Fox**: Coordinación general
- **Mike**: Investigación y análisis
- **Tom**: Gestión de proyectos
- **Karla**: Gestión de emails
- **Sarah**: Gestión de calendario

## Estructura del Proyecto
```
lucius_fox/
├── agents/          # Implementación de los agentes
├── futures/         # Documentación de futuras implementaciones
├── docs/            # Documentación técnica
├── credentials/     # Credenciales de servicios externos
├── scripts/         # Scripts de utilidad y deployment
├── deploy_credentials/ # Credenciales preparadas para deployment
├── Dockerfile       # Configuración de Docker
├── .dockerignore    # Archivos excluidos del contexto de Docker
├── requirements.txt # Dependencias
└── .gitignore       # Archivos excluidos del control de versiones
```

Para más detalles técnicos, consultar la [documentación](docs/).

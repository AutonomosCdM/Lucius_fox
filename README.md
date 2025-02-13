# Sistema Autónomo Lucius Fox

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
├── requirements.txt # Dependencias
└── .gitignore       # Archivos excluidos del control de versiones
```

Para más detalles técnicos, consultar la [documentación](docs/).

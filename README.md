# Agente de Análisis de Ventas con Inteligencia Artificial

Este proyecto implementa un **Agente Inteligente de Análisis de Ventas** utilizando la arquitectura de **Agentic AI** y el **Model Context Protocol (MCP)**. El agente permite interactuar con una base de datos SQLite mediante lenguaje natural, ejecutar consultas SQL automatizadas, generar gráficos interactivos con Plotly y exportar reportes en formatos Excel y CSV dentro de la carpeta `resultados/`.

---

## Arquitectura del Sistema

El sistema sigue una arquitectura modular basada en el protocolo **MCP**:

1. **Servidor MCP (`mcp_server.py`)**: Construido con **FastMCP**, expone herramientas para:
   - Consultar el esquema de la base de datos (`get_sales_schema`).
   - Ejecutar consultas SQL SELECT (`execute_sales_query`).
   - Generar gráficos interactivos con Plotly (`generate_sales_chart`).
   - Exportar resultados a CSV y Excel (`export_sales_to_file`).
   - Guardar automáticamente todas las salidas en el directorio `resultados/`.

2. **Agente ReAct / LangGraph (`agent.py`)**:
   - Conecta con el servidor MCP mediante `stdio` utilizando `MultiServerMCPClient`.
   - Utiliza **Amazon Bedrock** (`amazon.nova-lite-v1:0`) como Modelo de Lenguaje (LLM).
   - Mantiene memoria conversacional con `InMemorySaver`.

3. **Base de Datos (`ventas.db`)**:
   - Base de datos relacional SQLite que almacena las transacciones con los campos: `id`, `vendedor`, `sede`, `producto`, `cantidad`, `precio`, `fecha`.

---

## Requisitos Previos

- **Python 3.10+** (compatible con 3.12 / 3.14).
- **Git** instalado.
- **AWS CLI** configurado con acceso a Amazon Bedrock.

---

## Guía de Instalación y Configuración

### 1. Crear y Activar el Entorno Virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar Dependencias
Asegúrate de tener el archivo `requirements.txt`:
```text
mcp
langchain-mcp-adapters
langchain
langgraph
langchain-aws
boto3
pandas
plotly
openpyxl
```

Instala los paquetes necesarios:
```bash
pip install --upgrade -r requirements.txt
```

---

## Autenticación en AWS

Antes de ejecutar el agente, activa tu sesión de AWS en la terminal:

```bash
aws sso login
export AWS_REGION="us-east-1"
```

---

## Estructura del Proyecto

```text
.
├── .gitignore
├── README.md
├── requirements.txt
├── ventas.db
├── mcp_server.py
├── agent.py
└── resultados/          <-- Carpeta autogenerada para gráficos y archivos
    ├── *.html
    ├── *.xlsx
    └── *.csv
```

---

## Ejecución del Proyecto

Para ejecutar la prueba del agente:

```bash
python agent.py
```

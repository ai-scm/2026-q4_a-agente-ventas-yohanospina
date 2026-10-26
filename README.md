# 📊 Agente de Análisis de Ventas con Inteligencia Artificial (MCP + LangChain + Amazon Bedrock)

Este proyecto implementa un **Agente Inteligente de Análisis de Ventas** utilizando la arquitectura de **Agentic AI** y el **Model Context Protocol (MCP)**. El agente permite interactuar con una base de datos SQLite mediante lenguaje natural, ejecutar consultas SQL automatizadas, generar gráficos interactivos con Plotly y exportar reportes en formatos Excel y CSV dentro de la carpeta `resultados/`.

---

## 🏗️ Arquitectura del Sistema

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

## 🚀 Requisitos Previos

- **Python 3.10+** (compatible con 3.12 / 3.14).
- **Git** instalado.
- **AWS CLI** configurado con acceso a Amazon Bedrock (mediante AWS SSO o llaves de acceso).

---

## 🛠️ Guía de Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone https://github.com/<tu-usuario>/<nombre-repositorio>.git
cd <nombre-repositorio>
```

### 2. Crear y Activar el Entorno Virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias
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

## 🔑 Autenticación en AWS (Amazon Bedrock)

Antes de ejecutar el agente, activa tu sesión de AWS en la terminal:

```bash
aws sso login
export AWS_REGION="us-east-1"
```

---

## 📂 Estructura del Proyecto

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

## 📝 Código Fuente Principal

### 1. Servidor MCP (`mcp_server.py`)
```python
import os
import sqlite3
import pandas as pd
import plotly.express as px
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SalesAnalyticsService")

DB_PATH = "ventas.db"
OUTPUT_DIR = "resultados"

os.makedirs(OUTPUT_DIR, exist_ok=True)

@mcp.tool()
def get_sales_schema() -> str:
    """Retorna el esquema DDL de la base de datos de ventas."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return "\n".join([table for table in tables if table])

@mcp.tool()
def execute_sales_query(query: str) -> str:
    """Ejecuta una consulta SQL SELECT sobre la base de datos de ventas y retorna JSON."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_json(orient="records")
    except Exception as e:
        conn.close()
        return f"Error ejecutando la consulta SQL: {str(e)}"

@mcp.tool()
def generate_sales_chart(query: str, chart_type: str, x_col: str, y_col: str, title: str, filename: str) -> str:
    """Ejecuta una consulta SQL, genera un gráfico Plotly y lo guarda en 'resultados'."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return "La consulta no retornó datos para graficar."

        if chart_type.lower() == "bar":
            fig = px.bar(df, x=x_col, y=y_col, title=title)
        elif chart_type.lower() == "line":
            fig = px.line(df, x=x_col, y=y_col, title=title)
        elif chart_type.lower() == "pie":
            fig = px.pie(df, names=x_col, values=y_col, title=title)
        else:
            fig = px.bar(df, x=x_col, y=y_col, title=title)
            
        filepath = os.path.join(OUTPUT_DIR, filename)
        fig.write_html(filepath)
        return f"Gráfico generado exitosamente y guardado en '{filepath}'"
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return f"Error generando el gráfico: {str(e)}"

@mcp.tool()
def export_sales_to_file(query: str, format: str, filename: str) -> str:
    """Ejecuta una consulta SQL y exporta los resultados a CSV o Excel dentro de 'resultados'."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return "La consulta no retornó datos para exportar."

        filepath = os.path.join(OUTPUT_DIR, filename)

        if format.lower() == "excel":
            df.to_excel(filepath, index=False)
        else:
            df.to_csv(filepath, index=False)
            
        return f"Datos exportados exitosamente a '{filepath}'"
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        return f"Error exportando datos: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 2. Agente Principal (`agent.py`)
```python
import asyncio
import os
import sys

from langchain_aws import ChatBedrockConverse
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent


async def run_agent():
    mcp_client = MultiServerMCPClient(
        {
            "sales_service": {
                "command": sys.executable,
                "args": ["mcp_server.py"],
                "transport": "stdio",
            }
        }
    )

    tools = await mcp_client.get_tools()

    region = os.getenv("AWS_REGION", "us-east-1")
    llm = ChatBedrockConverse(
        model="amazon.nova-lite-v1:0", region_name=region, temperature=0
    )

    system_prompt = (
        "Eres un Agente Experto en Analítica de Ventas e Inteligencia de Negocios.\n"
        "Cuentas con acceso a herramientas conectadas mediante MCP a la base de datos relacional de la empresa.\n"
        "Reglas de operación:\n"
        "1. Revisa el esquema de la base de datos si requieres conocer el nombre de las columnas.\n"
        "2. Traduce las preguntas del usuario a consultas SQL válidas en sintaxis SQLite.\n"
        "3. Detecta automáticamente la intención detrás de la instrucción sin esperar palabras clave estrictas.\n"
        "4. Si el usuario solicita un gráfico, genera la consulta SQL, recupera los datos y llama a la herramienta de gráficos.\n"
        "5. Si el usuario pide guardar o exportar información, ejecuta la consulta y exporta los datos a CSV o Excel según corresponda.\n"
        "6. Ofrece explicaciones claras y tablas estructuradas en Markdown para acompañar los resultados.\n"
        "7. Guarda los archivos generados en la carpeta resultados y proporciona la ruta al usuario."
    )

    checkpoint_memory = InMemorySaver()

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        checkpointer=checkpoint_memory,
    )

    thread_config = {"configurable": {"thread_id": "sesion_analisis_ventas"}}

    print("=== Agente de Análisis de Ventas Operativo ===")

    prompt_usuario = "Genera un gráfico de barras con los productos más vendidos en Medellín y exporta el resultado a un archivo Excel."
    print(f"\n[Usuario]: {prompt_usuario}")

    inputs = {"messages": [("user", prompt_usuario)]}
    response = await agent.ainvoke(inputs, config=thread_config)

    ultimo_mensaje = response["messages"][-1]
    print(f"\n[Agente]: {ultimo_mensaje.content}")


if __name__ == "__main__":
    asyncio.run(run_agent())
```

---

## ⚡ Ejecución del Proyecto

Para ejecutar la prueba del agente:

```bash
python agent.py
```

### Resultados Generados
- Gráfico interactivo en `resultados/grafico_productos_mas_vendidos.html`.
- Reporte en Excel en `resultados/productos_mas_vendidos_medellin.xlsx`.

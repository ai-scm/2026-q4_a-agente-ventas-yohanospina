import asyncio
import os
import sys

from langchain_aws import ChatBedrockConverse
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
from langgraph.prebuilt import create_react_agent


async def run_agent():
    # Inicialización del cliente MCP conectado al servidor local mcp_server.py
    mcp_client = MultiServerMCPClient(
        {
            "sales_service": {
                "command": sys.executable,
                "args": ["mcp_server.py"],
                "transport": "stdio",
            }
        }
    )

    # Cargar dinámicamente las herramientas expuestas por el servidor FastMCP
    tools = await mcp_client.get_tools()

    # Configuración del modelo de lenguaje en Amazon Bedrock
    region = os.getenv("AWS_REGION", "us-east-1")
    llm = ChatBedrockConverse(
        model="amazon.nova-lite-v1:0", region_name=region, temperature=0
    )

    # Instrucciones de negocio para el agente
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

    # Memoria conversacional
    checkpoint_memory = InMemorySaver()

    # Creación del agente ReAct con LangGraph
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        checkpointer=checkpoint_memory,
    )

    thread_config = {"configurable": {"thread_id": "sesion_analisis_ventas"}}

    print("=== Agente de Análisis de Ventas Operativo ===")

    # Consulta de prueba para evaluación
    prompt_usuario = "Genera un gráfico de barras con los productos más vendidos en Medellín y exporta el resultado a un archivo Excel."
    print(f"\n[Usuario]: {prompt_usuario}")

    inputs = {"messages": [("user", prompt_usuario)]}
    response = await agent.ainvoke(inputs, config=thread_config)

    ultimo_mensaje = response["messages"][-1]
    print(f"\n[Agente]: {ultimo_mensaje.content}")


if __name__ == "__main__":
    asyncio.run(run_agent())
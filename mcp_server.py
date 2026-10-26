import os
import sqlite3
from mcp.server.fastmcp import FastMCP
import pandas as pd
import plotly.express as px

# Inicializar servidor FastMCP
mcp = FastMCP("SalesAnalyticsService")
DB_PATH = "ventas.db"
OUTPUT_DIR = "resultados"

# Asegurar que la carpeta de resultados exista
os.makedirs(OUTPUT_DIR, exist_ok=True)


@mcp.tool()
def get_sales_schema() -> str:
    """Retorna el esquema DDL de la base de datos de ventas."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return "\n".join([table[0] for table in tables if table[0]])


@mcp.tool()
def execute_sales_query(query: str) -> str:
    """Ejecuta una consulta SQL SELECT sobre la base de datos de ventas y retorna los resultados en formato JSON."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_json(orient="records")
    except Exception as e:
        conn.close()
        return f"Error ejecutando la consulta SQL: {str(e)}"


@mcp.tool()
def generate_sales_chart(
    query: str,
    chart_type: str,
    x_col: str,
    y_col: str,
    title: str,
    filename: str,
) -> str:
    """Ejecuta una consulta SQL, genera un gráfico interactivo con Plotly y lo guarda en HTML dentro de 'resultados'."""
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
        if "conn" in locals():
            conn.close()
        return f"Error generando el gráfico: {str(e)}"


@mcp.tool()
def export_sales_to_file(query: str, format: str, filename: str) -> str:
    """Ejecuta una consulta SQL y exporta los resultados a un archivo CSV o Excel dentro de 'resultados'."""
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
        if "conn" in locals():
            conn.close()
        return f"Error exportando datos: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
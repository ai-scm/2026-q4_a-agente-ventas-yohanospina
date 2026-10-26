import os
import sqlite3

DB_PATH = "ventas.db"


def init_database():
    # Eliminar la base de datos previa si existe para garantizar un entorno limpio
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Creación de la estructura relacional de la tabla de ventas
    cursor.execute("""
    CREATE TABLE ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendedor TEXT NOT NULL,
        sede TEXT NOT NULL,
        producto TEXT NOT NULL,
        cantidad INTEGER NOT NULL CHECK(cantidad > 0),
        precio REAL NOT NULL CHECK(precio >= 0),
        fecha DATE NOT NULL
    );
    """)

    # Registros de ventas de prueba para evaluación comercial
    datos_ejemplo = [
        ("Carlos Gómez", "Medellín", "Laptop Pro 15", 5, 1200.00, "2024-01-15"),
        ("Carlos Gómez", "Medellín", "Monitor 4K", 8, 350.00, "2024-01-20"),
        ("Ana Martínez", "Medellín", "Teclado Mecánico", 15, 80.00, "2024-02-01"),
        ("Ana Martínez", "Medellín", "Laptop Pro 15", 3, 1200.00, "2024-02-10"),
        ("Luisa Fernanda", "Bogotá", "Mouse Inalámbrico", 25, 25.00, "2024-01-10"),
        ("Luisa Fernanda", "Bogotá", "Laptop Pro 15", 7, 1200.00, "2024-01-22"),
        ("Jorge Ramos", "Bogotá", "Monitor 4K", 12, 350.00, "2024-02-05"),
        ("Jorge Ramos", "Bogotá", "Silla Ergonómica", 4, 250.00, "2024-02-18"),
        ("Diana Torres", "Cali", "Laptop Pro 15", 2, 1200.00, "2024-01-12"),
        ("Diana Torres", "Cali", "Teclado Mecánico", 10, 80.00, "2024-01-25"),
        ("Diana Torres", "Cali", "Mouse Inalámbrico", 18, 25.00, "2024-02-14"),
    ]

    cursor.executemany("""
    INSERT INTO ventas (vendedor, sede, producto, cantidad, precio, fecha)
    VALUES (?, ?, ?, ?, ?, ?);
    """, datos_ejemplo)

    conn.commit()
    conn.close()
    print("Base de datos 'ventas.db' creada y poblada exitosamente.")


if __name__ == "__main__":
    init_database()
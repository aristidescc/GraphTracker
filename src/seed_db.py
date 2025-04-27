import os
import sqlite3
import sys
from pathlib import Path

def seed_database():
    # Asegurar que estamos en el directorio correcto
    script_dir = Path(__file__).parent  # Directorio donde está seed_db.py
    instance_dir =  f"{script_dir}/instance"
    print(instance_dir)
    print(script_dir)
    db_path = f"{instance_dir }/graph.db"
    sql_path =  f"{instance_dir }/seed.sql"

    # Verificar si el archivo SQL existe
    if not os.path.exists(sql_path):
        print(f"Error: Archivo SQL no encontrado en {sql_path}")
        sys.exit(1)

    # Leer el contenido del archivo SQL
    with open(sql_path, 'r', encoding='utf-8') as file:
        sql_script = file.read()

    # Conectar a la base de datos
    print(f"Conectando a la base de datos: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Ejecutar el script SQL
        print("Ejecutando script SQL...")
        cursor.executescript(sql_script)

        # Confirmar los cambios
        conn.commit()
        print("Base de datos poblada exitosamente.")

    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    seed_database()
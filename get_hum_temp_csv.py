#!/usr/bin/python3
"""
Script para descargar datos de temperatura y humedad de una base de datos MySQL remota
usando credenciales y una consulta SQL filtrada por año.

Uso:
    python3 get_hum_temp_csv.py --host HOST --user USER --pass PASSWORD --db DATABASE --year YEAR

Guarda los resultados en data/HumTemp_YEAR.csv
"""

import argparse
import csv
import MySQLdb

def parse_args():
    parser = argparse.ArgumentParser(description="Descarga datos de temperatura y humedad de una base de datos MySQL remota.")
    parser.add_argument('--host', required=True, help='Host de la base de datos')
    parser.add_argument('--user', required=True, help='Usuario de la base de datos')
    parser.add_argument('--pwd', required=True, help='Contraseña de la base de datos')
    parser.add_argument('--db', required=True, help='Nombre de la base de datos')
    parser.add_argument('--year', type=int, required=True, help='Año a consultar')
    return parser.parse_args()

def main():
    args = parse_args()

    # Conexión a la base de datos MySQL
    conn = MySQLdb.connect(
        host=args.host,
        user=args.user,
        passwd=args.pwd,
        db=args.db
    )
    cursor = conn.cursor()

    # Consulta SQL
    sql = f"""
        SELECT ts, temp, hum
        FROM wheatherlog
        WHERE YEAR(ts) = {args.year}
        ORDER BY ts
    """

    cursor.execute(sql)
    rows = cursor.fetchall()

    # Guardar resultados en CSV
    output_file = f"data/HumTemp_{args.year}.csv"
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ts', 'temp', 'hum'])
        for row in rows:
            writer.writerow(row)

    print(f"Datos guardados en {output_file}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()


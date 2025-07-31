#!/usr/bin/env python3
"""
Autor: Pablo H.
Fecha: 07/25

Descripción:
Descarga archivos de IWV desde el IGN, los convierte a CSV y los guarda en ./data.

- Descarga los archivos especificados en data_files.
- Convierte cada archivo de texto a CSV con columnas: fecha, valor.
- Guarda los CSV en el directorio ./data.
- El archivo TXT descargado se elimina tras la conversión.

Uso:
$ python3 get_gnss_csv.py
"""

import os
import csv
import wget
import sys

# Opción de ayuda
if '-h' in sys.argv or '--help' in sys.argv:
    print("Este script no toma parámetros, solo actualiza los datos del GNSS")
    sys.exit(0)

# Lista de archivos a descargar
data_files = ["YEB1_pwv.txt", "YEBE_pwv.txt"]

# URL base de descarga
url = "https://datos-geodesia.ign.es/Utilidades/compresores/IWV/"

# Directorio de salida para los CSV
output_dir = "./data"
os.makedirs(output_dir, exist_ok=True)

for file in data_files:
    print(f"Descargando {file}...")
    input_file = wget.download(url + file)
    print(f"\nProcesando {input_file}...")

    output_file = os.path.join(output_dir, os.path.splitext(file)[0] + ".csv")

    # Si el archivo CSV ya existe, lo sobreescribe
    if os.path.exists(output_file):
        print(f"El archivo {output_file} ya existe y será sobreescrito.")

    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["fecha", "valor"])  # Cabecera CSV

        for line in infile:
            fields = line.strip().split()
            if len(fields) != 6:
                continue  # Salta líneas mal formateadas

            year, month, day, hour, minute, value = fields
            formatted_date = f"{int(year):04d}-{int(month):02d}-{int(day):02d} {int(hour):02d}:{int(minute):02d}:00"
            writer.writerow([formatted_date, value])

    # Elimina el archivo TXT descargado
    os.remove(input_file)
    print(f"Archivo temporal {input_file} eliminado.")
    print(f"Conversión completada. El archivo CSV se ha guardado como '{output_file}'.")

print("Terminado")

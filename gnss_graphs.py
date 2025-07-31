#!/usr/bin/python3
"""
Autor: Pablo H.
Fecha: 07/25

Descripción:
Procesa y grafica los valores de IWV (Integrated Water Vapor) obtenidos por las estaciones GNSS del Observatorio de Yebes.

Funcionamiento:
- Lee uno o más archivos CSV con datos de IWV, cada uno de una estación.
- Filtra los datos para el año especificado y añade datos de los extremos del año anterior/siguiente para mejorar la media móvil.
- Calcula y grafica los valores originales y la media móvil centrada de IWV para cada estación.
- Calcula una serie combinada promediando los valores de IWV de todas las estaciones para cada fecha, y grafica tanto la serie combinada como su media móvil centrada.
- Guarda las gráficas y el archivo de medias en formato CSV.

Uso:
    python3 gnss_graphs.py -y YEAR -w WINDOW -f file1.csv file2.csv ...
"""

import csv
import argparse
from datetime import datetime
from typing import List, Dict
import matplotlib.pyplot as plt
import os

# Estructuras globales para almacenar los datos de cada estación y el resultado combinado
fechas_arrs: List[List[datetime]] = []
data_arrs: List[List[float]] = []
data_avg_arrs: List[List[float]] = []
final_result: Dict[datetime, float] = {}

def parse_args():
    """
    Parsea los argumentos de la terminal.
    -y YEAR: año a analizar
    -w WINDOW: tamaño de la ventana para la media móvil centrada
    -f FILES: lista de archivos CSV de entrada
    --show: si está presente, muestra los gráficos además de guardarlos
    """
    parser = argparse.ArgumentParser(description="Procesa y grafica valores de IWV de estaciones GNSS.")
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year, help='Año a analizar (por defecto, año actual)')
    parser.add_argument('-w', '--window', type=int, default=250, help='Tamaño de la ventana para la media móvil centrada')
    parser.add_argument('-f', '--files', nargs='+', required=True, help='Lista de archivos CSV de entrada')
    parser.add_argument('--show', action='store_true', help='Muestra los gráficos en pantalla además de guardarlos')
    return parser.parse_args()

def filter_date(fecha: datetime, year: int) -> bool:
    """
    Filtra fechas del año actual, últimos 15 días de diciembre anterior y primeros 15 días de enero siguiente.
    Esto mejora el cálculo de la media móvil en los extremos del año.
    """
    if fecha.year == year:
        return True
    if fecha.year == (year - 1) and fecha.month == 12 and fecha.day >= 15:
        return True
    if fecha.year == (year + 1) and fecha.month == 1 and fecha.day <= 15:
        return True
    return False

def avg_calc(date_arr: List[datetime], iwv_arr: List[float], window: int = 500, year: int = None) -> List[float]:
    """
    Calcula la media móvil centrada para los datos de IWV.
    Para cada punto, toma una ventana de tamaño 'window' a izquierda y derecha.
    """
    n = len(iwv_arr)
    result = []
    for pos, fecha in enumerate(date_arr):
        if year is None or fecha.year == year:
            left = max(0, pos - window)
            right = min(n, pos + window + 1)
            window_vals = iwv_arr[left:right]
            result.append(sum(window_vals) / len(window_vals))
    return result

def read_station_data(file: str, year: int) -> tuple:
    """
    Lee un archivo CSV de estación GNSS y devuelve:
    - fechas e IWV del año principal
    - fechas e IWV extendidas para la media móvil
    """
    curr_date_arr, curr_iwv_arr = [], []
    curr_date_arr_ext, curr_iwv_arr_ext = [], []

    with open(file, 'r') as cf:
        lector = csv.reader(cf)
        next(lector)  # Saltar encabezado
        for fila in lector:
            if not fila:
                continue
            fecha_str, valor_str = fila
            fecha = datetime.strptime(fecha_str.strip(), '%Y-%m-%d %H:%M:%S')
            iwv = float(valor_str.strip()) * 1000  # Convertir a mm

            if fecha.year == year:
                curr_date_arr.append(fecha)
                curr_iwv_arr.append(iwv)
                # Promediar para la serie combinada
                if fecha not in final_result:
                    final_result[fecha] = iwv
                else:
                    final_result[fecha] = (final_result[fecha] + iwv) / 2

            if filter_date(fecha, year):
                curr_date_arr_ext.append(fecha)
                curr_iwv_arr_ext.append(iwv)

    return curr_date_arr, curr_iwv_arr, curr_date_arr_ext, curr_iwv_arr_ext

def save_data(files: List[str], year: int, window: int):
    """
    Lee los archivos pasados y almacena los datos en las estructuras globales.
    """
    for curr_file in files:
        curr_date_arr, curr_iwv_arr, curr_date_arr_ext, curr_iwv_arr_ext = read_station_data(curr_file, year)
        fechas_arrs.append(curr_date_arr)
        data_arrs.append(curr_iwv_arr)
        data_avg_arrs.append(avg_calc(curr_date_arr_ext, curr_iwv_arr_ext, window, year))

def save_avg_data(fecha_arr: List[datetime], iwv_arr: List[float], year: int):
    """
    Guarda la serie combinada de medias en un archivo CSV.
    """
    os.makedirs("data", exist_ok=True)
    output_file = f"data/Avg_data_{year}.csv"
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["Time", "IWV"])
        for i in range(0, len(fecha_arr)):
            writer.writerow([fecha_arr[i], iwv_arr[i]])
    print(f"Nuevo fichero con las medias guardado en {output_file}")

def plot_station_data(files: List[str], year: int, window: int, show_plots: bool):
    """
    Grafica los datos originales y la media móvil de cada estación GNSS.
    Si show_plots es True, muestra los gráficos en pantalla.
    """
    plt.figure(figsize=(12, 6))
    plt.title(f"IWV GNSS values")
    plt.xlabel("Date")
    plt.ylabel("IWV (mm)")
    plt.xticks(rotation=45)
    plt.grid()
    for idx, (curr_dates, curr_data, curr_avg_data) in enumerate(zip(fechas_arrs, data_arrs, data_avg_arrs), start=1):
        label_base = files[idx - 1].split("/")[-1].split("_")[0]
        plt.plot(curr_dates, curr_data, linestyle='-', label=f'Data {label_base}')
        plt.plot(curr_dates, curr_avg_data, linestyle='-', label=f'Average {label_base}')
    plt.legend(loc='best')
    plt.tight_layout()
    os.makedirs("plots", exist_ok=True)
    plt.savefig(f"plots/iwv_plot_fuentes_{year}.png")
    if show_plots:
        plt.show()
    plt.close()

def plot_combined_data(year: int, window: int, show_plots: bool):
    """
    Grafica la serie combinada (media de estaciones) y su media móvil centrada.
    Si show_plots es True, muestra los gráficos en pantalla.
    """
    sorted_dates = sorted(final_result)
    values = [final_result[fecha] for fecha in sorted_dates]
    avg_values = avg_calc(sorted_dates, values, window, year)

    save_avg_data(sorted_dates, avg_values, year)

    plt.figure(figsize=(12, 6))
    plt.title("Zenith IWV values")
    plt.xlabel("Date")
    plt.ylabel("IWV (mm)")
    plt.xticks(rotation=45)
    plt.grid()
    plt.plot(sorted_dates, values, linestyle='-', color='c', label='Average value of GNSS stations')
    plt.plot(sorted_dates, avg_values, linestyle='-', color='red', label='Moving average')
    plt.legend(loc='best')
    plt.tight_layout()
    os.makedirs("plots", exist_ok=True)
    plt.savefig(f"plots/iwv_final_plot_{year}.png")
    if show_plots:
        plt.show()
    plt.close()

def main():
    """
    Flujo principal del script.
    """
    args = parse_args()
    save_data(args.files, args.year, args.window)
    plot_station_data(args.files, args.year, args.window, args.show)
    plot_combined_data(args.year, args.window, args.show)

if __name__ == "__main__":
    main()
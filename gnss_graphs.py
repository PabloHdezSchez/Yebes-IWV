#!/usr/bin/python3
"""
Autor: Pablo H.
Fecha: 07/25

Descripción:
Este script procesa y grafica los valores de IWV (Integrated Water Vapor) obtenidos por las dos estaciones GNSS instaladas en el Observatorio de Yebes.

Funcionamiento principal:
- Lee uno o más archivos CSV con datos de IWV, donde cada archivo corresponde a una estación diferente.
- Filtra los datos para el año especificado y también permite incluir los últimos 15 días de diciembre del año anterior y los primeros 15 días de enero del año siguiente para mejorar la media a principios y finales de año.
- Calcula y grafica los valores originales y la media móvil centrada de IWV para cada estación por separado.
- Calcula una serie combinada promediando los valores de IWV de ambas estaciones para cada fecha, y grafica tanto la serie combinada como su media móvil centrada.
- Guarda las gráficas generadas en archivos PNG.

Uso:
$ python3 gnss_graphs.py -y YEAR -w WINDOW -f file1.csv file2.csv ...
Cada archivo debe tener dos columnas: fecha (YYYY-MM-DD HH:MM:SS) e IWV (mm), con encabezado en la primera línea.
"""

import csv
import argparse
from datetime import datetime
from typing import List, Dict
import matplotlib.pyplot as plt

# Estructuras para almacenar los datos de cada archivo
fechas_arrs: List[List[datetime]] = []
data_arrs: List[List[float]] = []
data_avg_arrs: List[List[float]] = []
final_result: Dict[datetime, float] = {}

def parse_args():
    parser = argparse.ArgumentParser(description="Procesa y grafica valores de IWV de estaciones GNSS.")
    parser.add_argument('-y', '--year', type=int, default=datetime.now().year, help='Año a analizar (por defecto, año actual)')
    parser.add_argument('-w', '--window', type=int, default=250, help='Tamaño de la ventana para la media móvil centrada')
    parser.add_argument('-f', '--files', nargs='+', required=True, help='Lista de archivos CSV de entrada')
    return parser.parse_args()

def filter_date(fecha: datetime, year: int) -> bool:
    """
    Filtra fechas del año actual, últimos 15 días de diciembre anterior y primeros 15 días de enero siguiente.
    Hecho así para promediar mejor el inicio y final de año con datos anteriores y posteriores.
    """
    if fecha.year == year:
        return True
    if fecha.year == (year - 1) and fecha.month == 12 and fecha.day >= 15:
        return True
    if fecha.year == (year + 1) and fecha.month == 1 and fecha.day <= 15:
        return True
    return False

def avg_calc(date_arr: List[datetime], iwv_arr: List[float], window: int = 500, year: int = None) -> List[float]:
    """Calcula la media móvil centrada para los datos de IWV."""
    n = len(iwv_arr)
    result = []
    for pos, fecha in enumerate(date_arr):
        if year is None or fecha.year == year:
            left = max(0, pos - window)
            right = min(n, pos + window + 1)
            window_vals = iwv_arr[left:right]
            result.append(sum(window_vals) / len(window_vals))
    return result

def save_data(files: List[str], year: int, window: int):
    """Lee los archivos pasados y almacena los datos en las estructuras globales."""
    for curr_file in files:
        curr_date_arr, curr_iwv_arr = [], []
        curr_date_arr_ext, curr_iwv_arr_ext = [], []

        with open(curr_file, 'r') as cf:
            lector = csv.reader(cf)
            next(lector)  # Saltar encabezado
            for fila in lector:
                if not fila:
                    continue
                fecha_str, valor_str = fila
                fecha = datetime.strptime(fecha_str.strip(), '%Y-%m-%d %H:%M:%S')
                iwv = float(valor_str.strip()) * 1000

                if fecha.year == year:
                    curr_date_arr.append(fecha)
                    curr_iwv_arr.append(iwv)
                    if fecha not in final_result:
                        final_result[fecha] = iwv
                    else:
                        final_result[fecha] = (final_result[fecha] + iwv) / 2

                if filter_date(fecha, year):
                    curr_date_arr_ext.append(fecha)
                    curr_iwv_arr_ext.append(iwv)

        fechas_arrs.append(curr_date_arr)
        data_arrs.append(curr_iwv_arr)
        data_avg_arrs.append(avg_calc(curr_date_arr_ext, curr_iwv_arr_ext, window, year))

def save_avg_data(fecha_arr: List[datetime], iwv_arr: List[float], year: int):
    output_file = f"data/Avg_data_{year}.csv"
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["fecha", "IWV"])
        for i in range(0, len(fecha_arr)):
            writer.writerow([fecha_arr[i], iwv_arr[i]])
    print("Nuevo fichero con las medias guardado")
    return

def plot_data(files:List[str], year: int, window: int):
    """Genera y guarda las gráficas de los datos y del resultado final."""
    plt.figure(figsize=(10, 5))
    plt.title(f"Valores de IWV GNSS")
    plt.xlabel("Fecha")
    plt.ylabel("IWV (mm)")
    plt.xticks(rotation=45)
    plt.grid()
    for idx, (curr_dates, curr_data, curr_avg_data) in enumerate(zip(fechas_arrs, data_arrs, data_avg_arrs), start=1):
        plt.plot(curr_dates, curr_data, linestyle='-', label='Datos ' + files[idx - 1].split("/")[-1].split("_")[0])
        plt.plot(curr_dates, curr_avg_data, linestyle='-', label='Media de ' + files[idx - 1].split("/")[-1].split("_")[0])
    plt.legend(loc = 'best')
    plt.tight_layout()
    plt.savefig(f"plots/iwv_plot_fuentes_{year}.png")
    plt.show()

    # Gráfica final combinada con media móvil
    sorted_dates = sorted(final_result)
    values = [final_result[fecha] for fecha in sorted_dates]
    avg_values = avg_calc(sorted_dates, values, window, year)

    save_avg_data(sorted_dates, avg_values, year)

    plt.figure(figsize=(10, 5))
    plt.title("Valores de IWV Cenital")
    plt.xlabel("Fecha")
    plt.ylabel("IWV (mm)")
    plt.xticks(rotation=45)
    plt.grid()
    plt.plot(sorted_dates, values, linestyle='-', color='c')
    plt.plot(sorted_dates, avg_values, linestyle='-', color='red')
    plt.legend(['Media de las estaciones GNSS', 'Media movil'], loc='best')
    plt.tight_layout()
    plt.savefig(f"plots/iwv_final_plot_{year}.png")
    plt.show()

def main():
    args = parse_args()
    save_data(args.files, args.year, args.window)
    plot_data(args.files, args.year, args.window)

if __name__ == "__main__":
    main()
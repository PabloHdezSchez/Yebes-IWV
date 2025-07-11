#!/usr/bin/python3
"""
Autor: Pablo H.
Fecha: 07/25

Descripción:
Calcula y representa el IWV a partir de archivos de humedad y temperatura, y lo compara con los datos de Avg_data.csv.

Funcionamiento:
- Lee los archivos 'data/Humidity_YYYY.csv' y 'data/Temperature_YYYY.csv' con formato:
    "Time","Humedad Relativa"
    2025-01-01 00:00:00,80.13 %H
    ...
    "Time","Temperatura"
    2025-01-01 00:00:00,2.51 °C
    ...
- Limpia y convierte los valores numéricos.
- Une los datos por fecha/hora.
- Calcula el IWV para cada instante y lo guarda en un diccionario.
- Lee el archivo 'Avg_data.csv' con formato:
    fecha,IWV
    2025-01-01 02:00:00,12.59...
- Representa el IWV calculado (dos métodos) y el IWV de Avg_data.csv en la misma gráfica.

Uso:
    python3 iwv_graphs.py [-h] [-y YEAR] [-hf H_FACTOR]

Calcula y representa IWV a partir de humedad y temperatura.

options:
    -h, --help                  show this help message and exit
    -y YEAR, --year YEAR        Año de los datos a analizar
    -hf H_FACTOR, --h_factor    Factor de escala H
"""

import pandas as pd
import matplotlib.pyplot as plt
import argparse
import atm_iwv_calculator as atm_c

def parse_args():
    parser = argparse.ArgumentParser(description="Calcula y representa IWV a partir de humedad y temperatura.")
    parser.add_argument('-y', '--year', type=int, default=2025, help='Año de los datos a analizar')
    parser.add_argument('-hf', '--h_factor', type=float, default=2000, help='Factor de escala H')
    return parser.parse_args()


def plot_errors(df, df_avg, iwv_list, iwv_wh2o_list, H_SCALE_FACTOR):
    """
    Representa los errores absolutos entre:
    - Avg_data vs método clásico
    - Avg_data vs método wh2o
    - método clásico vs método wh2o
    Solo se consideran los puntos donde hay correspondencia temporal.
    """
    df_methods = pd.DataFrame({
        "Time": df["Time"],
        "IWV_clasico": iwv_list,
        "IWV_wh2o": iwv_wh2o_list
    }).set_index("Time")

    # Eliminar duplicados en el índice (mantener el primero)
    df_methods = df_methods[~df_methods.index.duplicated(keep='first')]
    df_avg = df_avg.set_index("fecha")
    df_avg = df_avg[~df_avg.index.duplicated(keep='first')]

    # Reindexar para que coincidan los tiempos
    df_methods_interp = df_methods.reindex(df_avg.index, method='nearest')

    # Cálculo de errores absolutos
    error_avg_clasico = (df_avg["IWV"] - df_methods_interp["IWV_clasico"]).abs()
    error_avg_wh2o = (df_avg["IWV"] - df_methods_interp["IWV_wh2o"]).abs()
    error_clasico_wh2o = (df_methods_interp["IWV_clasico"] - df_methods_interp["IWV_wh2o"]).abs()

    # Gráfica
    plt.figure(figsize=(12, 6))
    plt.plot(df_avg.index, error_avg_clasico, label="|Avg - Formula iwv|", color="red")
    # plt.plot(df_avg.index, error_avg_wh2o, label="|Avg - wh2o 40M|")
    # plt.plot(df_avg.index, error_clasico_wh2o, label="|Método clásico - Método wh2o|")
    plt.xlabel("Fecha")
    plt.ylabel("Error absoluto IWV")
    plt.title(f"Errores absolutos entre métodos de IWV (H Factor = {H_SCALE_FACTOR})")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(f"plots/error_iwv_{df_avg.index[0].year}_hf{H_SCALE_FACTOR}.png")
    plt.show()

def read_data(YEAR, H_SCALE_FACTOR):
    """
    Lee los ficheros de humedad, temperatura y avg_data, limpia los valores y calcula IWV por ambos métodos.
    Devuelve: df (merge humedad+temperatura), df_avg, iwv_list, iwv_wh2o_list
    """
    import atm_iwv_calculator as atm_c
    import pandas as pd

    # Leer humedad y limpiar valores
    df_hum = pd.read_csv(f"data/Humidity_{YEAR}.csv")
    df_hum["Time"] = pd.to_datetime(df_hum["Time"])
    df_hum["Humedad Relativa"] = df_hum["Humedad Relativa"].apply(lambda x: atm_c.clean_value(x, "%H"))

    # Leer temperatura y limpiar valores
    df_temp = pd.read_csv(f"data/Temperature_{YEAR}.csv")
    df_temp = df_temp.rename(columns={"Time": "Time", "Temperatura": "Temp"})
    df_temp["Time"] = pd.to_datetime(df_temp["Time"])
    df_temp["Temp"] = df_temp["Temp"].apply(lambda x: atm_c.clean_value(x, "°C"))

    # Unir por fecha/hora (asegurando que ambas columnas sean datetime)
    df = pd.merge(df_hum, df_temp, on="Time", how="inner")

    # Calcular IWV por ambos métodos y guardar en listas
    iwv_list = []
    iwv_wh2o_list = []
    for _, row in df.iterrows():
        iwv = atm_c.calc_iwv(row["Temp"], H_SCALE_FACTOR, row["Humedad Relativa"])
        iwv_wh2o = atm_c.calc_iwv_wh2o(row["Temp"], row["Humedad Relativa"], H_SCALE_FACTOR)
        iwv_list.append(iwv)
        iwv_wh2o_list.append(iwv_wh2o)

    # Leer y preparar Avg_data.csv
    df_avg = pd.read_csv(f"data/Avg_data_{YEAR}.csv")
    df_avg["fecha"] = pd.to_datetime(df_avg["fecha"])

    return df, df_avg, iwv_list, iwv_wh2o_list

def main():
    args = parse_args()
    YEAR = args.year
    H_SCALE_FACTOR = args.h_factor

    # Leer y calcular datos usando la nueva función
    df, df_avg, iwv_list, iwv_wh2o_list = read_data(YEAR, H_SCALE_FACTOR)

    # Representar IWV calculado y Avg_data.csv
    plt.figure(figsize=(12, 6))
    plt.plot(df["Time"], iwv_list, label=f"IWV mediante formula (H={H_SCALE_FACTOR})")
    # plt.plot(df["Time"], iwv_wh2o_list, label=f"IWV codigo 40M (H={H_SCALE_FACTOR})")
    plt.plot(df_avg["fecha"], df_avg["IWV"], color='red', label="IWV Avg_data.csv")
    plt.xlabel("Fecha")
    plt.ylabel("IWV")
    plt.title(f"IWV calculado vs IWV {YEAR} (H Factor = {H_SCALE_FACTOR})")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(f"plots/iwv_calculado_vs_avg_{YEAR}_hf{H_SCALE_FACTOR}.png")
    plt.show()

    # Graficar errores
    plot_errors(df, df_avg, iwv_list, iwv_wh2o_list, H_SCALE_FACTOR)

if __name__ == "__main__":
    main()

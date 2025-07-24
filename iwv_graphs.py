#!/usr/bin/python3
"""
Autor: Pablo H.
Fecha: 07/25

Descripción:
Calcula y representa el IWV a partir de archivos de humedad y temperatura, y lo compara con los datos de Avg_data.csv.

Funcionamiento:
- Lee los archivos 'data/Humidity_YYYY.csv' y 'data/Temperature_YYYY.csv'.
- Limpia y convierte los valores numéricos.
- Une los datos por fecha/hora.
- Calcula el IWV para cada instante por dos métodos.
- Guarda los resultados en CSV.
- Lee el archivo 'Avg_data_YYYY.csv' y representa los IWV calculados junto al dato de referencia.
- Grafica los errores absolutos entre métodos y referencia.

Uso:
    python3 iwv_graphs.py [-h] [-y YEAR] [-hf H_FACTOR]
"""

import pandas as pd
import matplotlib.pyplot as plt
import argparse
import atm_iwv_calculator as atm_c
import os

def parse_args():
    """Parsea los argumentos de la terminal."""
    parser = argparse.ArgumentParser(description="Calcula y representa IWV a partir de humedad y temperatura.")
    parser.add_argument('-y', '--year', type=int, default=2025, help='Año de los datos a analizar')
    parser.add_argument('-hf', '--h_factor', type=float, default=2000, help='Factor de escala H')
    return parser.parse_args()

def load_humidity(year):
    """Carga y limpia el fichero de humedad."""
    df_hum = pd.read_csv(f"data/Humidity_{year}.csv")
    df_hum["Time"] = pd.to_datetime(df_hum["Time"])
    df_hum["Humedad Relativa"] = df_hum["Humedad Relativa"].apply(lambda x: atm_c.clean_value(x, "%H"))
    return df_hum

def load_temperature(year):
    """Carga y limpia el fichero de temperatura."""
    df_temp = pd.read_csv(f"data/Temperature_{year}.csv")
    df_temp = df_temp.rename(columns={"Time": "Time", "Temperatura": "Temp"})
    df_temp["Time"] = pd.to_datetime(df_temp["Time"])
    df_temp["Temp"] = df_temp["Temp"].apply(lambda x: atm_c.clean_value(x, "°C"))
    return df_temp

def load_avg_data(year):
    """Carga el fichero de IWV de referencia."""
    df_avg = pd.read_csv(f"data/Avg_data_{year}.csv")
    df_avg["fecha"] = pd.to_datetime(df_avg["fecha"])
    return df_avg

def calculate_iwv(df, h_scale_factor):
    """Calcula IWV por ambos métodos y añade columna IWV al DataFrame."""
    iwv_list = []
    for _, row in df.iterrows():
        iwv = atm_c.calc_iwv(row["Temp"], h_scale_factor, row["Humedad Relativa"])
        iwv_list.append(iwv)
    df["IWV"] = iwv_list
    return iwv_list

def save_iwv_results(df, year, h_scale_factor):
    """Guarda los resultados de IWV en un CSV."""
    output_file = f"data/IWV_calculado_{year}_hf{h_scale_factor}.csv"
    df.to_csv(output_file, index=False)
    print(f"Resultados IWV guardados en {output_file}")

def plot_iwv(df, df_avg, iwv_list, year, h_scale_factor):
    """Grafica los IWV calculados y los de referencia."""
    plt.figure(figsize=(12, 6))
    plt.plot(df["Time"], iwv_list, label=f"IWV fórmula (H={h_scale_factor})")
    plt.plot(df_avg["fecha"], df_avg["IWV"], color='red', label="IWV Avg_data.csv")
    plt.xlabel("Fecha")
    plt.ylabel("IWV")
    plt.title(f"IWV calculado vs IWV referencia {year} (H Factor = {h_scale_factor})")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    os.makedirs("plots", exist_ok=True)
    plt.savefig(f"plots/iwv_calculado_vs_avg_{year}_hf{h_scale_factor}.png")
    plt.show()

def plot_errors(df, df_avg, iwv_list, h_scale_factor):
    """
    Grafica los errores absolutos entre:
    - Avg_data vs método clásico
    - Avg_data vs método wh2o
    - método clásico vs método wh2o
    """
    df_methods = pd.DataFrame({
        "Time": df["Time"],
        "IWV_clasico": iwv_list
    }).set_index("Time")

    # Eliminar duplicados en el índice (mantener el primero)
    df_methods = df_methods[~df_methods.index.duplicated(keep='first')]
    df_avg = df_avg.set_index("fecha")
    df_avg = df_avg[~df_avg.index.duplicated(keep='first')]

    # Reindexar para que coincidan los tiempos
    df_methods_interp = df_methods.reindex(df_avg.index, method='nearest')

    # Cálculo de errores absolutos
    error_avg_clasico = (df_avg["IWV"] - df_methods_interp["IWV_clasico"]).abs()

    # Gráfica
    plt.figure(figsize=(12, 6))
    plt.plot(df_avg.index, error_avg_clasico, label=f"|Avg - Formula iwv| (H={h_scale_factor})", color="red")
    plt.xlabel("Fecha")
    plt.ylabel("Error absoluto IWV")
    plt.title(f"Errores absolutos de IWV (H Factor = {h_scale_factor})")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    os.makedirs("plots", exist_ok=True)
    plt.savefig(f"plots/error_iwv_{df_avg.index[0].year}_hf{h_scale_factor}.png")
    plt.show()

def main():
    args = parse_args()
    year = args.year
    h_scale_factor = args.h_factor

    # Cargar datos
    df_hum = load_humidity(year)
    df_temp = load_temperature(year)
    df_avg = load_avg_data(year)

    # Unir por fecha/hora
    df = pd.merge(df_hum, df_temp, on="Time", how="inner")

    # Calcular IWV
    iwv_list = calculate_iwv(df, h_scale_factor)

    # Guardar resultados
    save_iwv_results(df, year, h_scale_factor)

    # Graficar IWV y errores
    plot_iwv(df, df_avg, iwv_list, year, h_scale_factor)
    plot_errors(df, df_avg, iwv_list, h_scale_factor)

if __name__ == "__main__":
    main()

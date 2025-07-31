#!/usr/bin/python3
"""
Autor: Pablo H.
Fecha: 07/25

Descripción:
Calcula y representa el IWV a partir de un archivo combinado de humedad y temperatura, y lo compara con los datos de Avg_data.csv.

Funcionamiento:
- Lee el archivo 'data/HumTemp_{year}.csv' con columnas ts, temp, hum.
- Filtra solo los datos a las horas: en punto, cuarto, media y menos cuarto.
- Limpia y convierte los valores numéricos.
- Calcula el IWV para cada instante por el método especificado.
- Guarda los resultados en CSV.
- Lee el archivo 'Avg_data_{year}.csv' y representa los IWV calculados junto al dato de referencia.
- Grafica los errores absolutos entre métodos y referencia.

Uso:
    python3 iwv_graphs.py [-h] [-y YEAR] [-hf H_FACTOR] [--show]
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
    parser.add_argument('--show', action='store_true', help='Muestra los gráficos en pantalla además de guardarlos')
    return parser.parse_args()

def filter_quarter_hours(df):
    """
    Filtra el DataFrame para mantener solo las horas: en punto (00), cuarto (15), media (30) y menos cuarto (45).
    """
    df['Time'] = pd.to_datetime(df['Time'])
    # Filtrar por minutos: 00, 15, 30, 45
    quarter_hours = df[df['Time'].dt.minute.isin([0, 15, 30, 45])]
    return quarter_hours

def load_humtemp(year):
    """Carga y limpia el fichero combinado de humedad y temperatura."""
    df = pd.read_csv(f"data/HumTemp_{year}.csv")
    df["ts"] = pd.to_datetime(df["ts"])
    df = df.rename(columns={"ts": "Time", "temp": "Temp", "hum": "Humedad Relativa"})
    # Filtrar solo datos de cuartos de hora
    df = filter_quarter_hours(df)
    return df

def load_avg_data(year):
    """Carga el fichero de IWV de referencia."""
    df_avg = pd.read_csv(f"data/Avg_data_{year}.csv")
    df_avg["Time"] = pd.to_datetime(df_avg["Time"])
    # Filtrar solo datos de cuartos de hora
    df_avg = filter_quarter_hours(df_avg)
    return df_avg

def calculate_iwv(df, h_scale_factor):
    """Calcula IWV por el método clásico y añade columna IWV al DataFrame."""
    iwv_list = []
    for _, row in df.iterrows():
        iwv = atm_c.calc_iwv(row["Temp"], h_scale_factor, row["Humedad Relativa"])
        iwv_list.append(iwv)
    df["IWV"] = iwv_list
    return iwv_list

def save_iwv_results(df, year, h_scale_factor):
    """Guarda los resultados de IWV en un CSV."""
    output_file = f"data/IWV_calculado_{year}_hf{int(h_scale_factor)}.csv"
    df.to_csv(output_file, index=False)
    print(f"Resultados IWV guardados en {output_file}")

def plot_iwv(df, df_avg, iwv_list, year, h_scale_factor, show_plots):
    """Grafica los IWV calculados y los de referencia."""
    plt.figure(figsize=(12, 6))
    plt.plot(df_avg["Time"], df_avg["IWV"], label="IWV de GNSS")
    plt.plot(df["Time"], iwv_list, label=f"Parámetros atmosféricos (H={h_scale_factor})")
    plt.xlabel("Fecha")
    plt.ylabel("IWV")
    plt.title(f"IWV calculado vs IWV referencia {year} (H Factor = {h_scale_factor})")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    os.makedirs("plots", exist_ok=True)
    plt.savefig(f"plots/iwv_calculado_vs_avg_{year}_hf{int(h_scale_factor)}.png")
    if show_plots:
        plt.show()
    plt.close()

def plot_errors(df, df_avg, iwv_list, h_scale_factor, show_plots):
    """
    Grafica los errores absolutos entre:
    - Avg_data vs método clásico
    """
    df_methods = pd.DataFrame({
        "Time": df["Time"],
        "IWV_clasico": iwv_list
    }).set_index("Time")

    # Eliminar duplicados en el índice (mantener el primero)
    df_methods = df_methods[~df_methods.index.duplicated(keep='first')]
    df_avg = df_avg.set_index("Time")
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
    plt.savefig(f"plots/error_iwv_{df_avg.index[0].year}_hf{int(h_scale_factor)}.png")
    if show_plots:
        plt.show()
    plt.close()

def main():
    args = parse_args()
    year = args.year
    h_scale_factor = args.h_factor
    show_plots = args.show

    # Cargar datos
    df = load_humtemp(year)
    df_avg = load_avg_data(year)

    # Calcular IWV
    iwv_list = calculate_iwv(df, h_scale_factor)

    # Guardar resultados
    save_iwv_results(df, year, h_scale_factor)

    # Graficar IWV y errores
    plot_iwv(df, df_avg, iwv_list, year, h_scale_factor, show_plots)
    plot_errors(df, df_avg, iwv_list, h_scale_factor, show_plots)

if __name__ == "__main__":
    main()

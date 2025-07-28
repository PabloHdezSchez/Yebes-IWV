#!/usr/bin/python3
"""
Script para calcular la opacidad atmosférica a partir de ficheros de IWV usando el ejecutable ATM.

- Toma cualquier cantidad de ficheros CSV con columnas 'Time' e 'IWV'.
- Para cada valor de IWV y para cada frecuencia indicada, sustituye %0 (IWV) y %1 (frecuencia) en input.atm y ejecuta ./atm/atm.
- Extrae el valor de 'total atmospheric opacity' (primera columna) de la salida.
- Representa una curva de opacidad para cada fichero y frecuencia, con leyenda, y guarda la imagen en ./plots.

Uso:
    python3 opacity_graphs.py file1.csv file2.csv ... --freq 41.2,43.0 --period 5
"""

import argparse
import pandas as pd
import subprocess
import os
import matplotlib.pyplot as plt

ATM_EXEC = "./atm/atm"
ATM_INPUT_TEMPLATE = "./atm/input.atm"
PLOTS_DIR = "plots"

def parse_args():
    parser = argparse.ArgumentParser(description="Calcula la opacidad atmosférica usando ATM para varios ficheros de IWV y varias frecuencias.")
    parser.add_argument('files', nargs='+', help='Ficheros CSV con columnas Time e IWV')
    parser.add_argument('--period', type=int, default=1, help='Procesar solo una de cada N muestras (por defecto 1, es decir, todas)')
    parser.add_argument('--freq', required=True, help='Lista de frecuencias en GHz separadas por coma (ej: 41.2,43.0)')
    return parser.parse_args()

def run_atm_with_iwv_and_freq(iwv_value, freq_value, atm_input_template):
    """
    Sustituye todas las ocurrencias de %0 (IWV) y %1 (frecuencia) en el fichero input.atm y ejecuta ATM.
    Devuelve la salida del programa ATM.
    """
    # Leer plantilla
    with open(atm_input_template, 'r') as f:
        atm_input = f.read()
    atm_input_filled = atm_input.replace('%0', f"{iwv_value}").replace('%1', f"{freq_value}")

    # Ejecutar ATM pasando la entrada por stdin
    try:
        result = subprocess.run(
            [ATM_EXEC],
            input=atm_input_filled,
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando ATM para IWV={iwv_value}, freq={freq_value}: {e}")
        output = ""
    return output

def extract_opacity(atm_output):
    """
    Extrae el valor de 'total atmospheric opacity' (primera columna) de la salida de ATM.
    """
    for line in atm_output.splitlines():
        if line.strip().startswith("total atmospheric opacity"):
            # Ejemplo de línea: total atmospheric opacity    =      0.0773         0.0469
            parts = line.split("=")
            if len(parts) > 1:
                values = parts[1].split()
                try:
                    return float(values[0])
                except (IndexError, ValueError):
                    return None
    return None

def process_file(csv_file, atm_input_template, freq, period=1):
    """
    Procesa un fichero CSV, ejecuta ATM para cada IWV (cada 'period' muestras) y devuelve listas de fechas y opacidades.
    """
    df = pd.read_csv(csv_file)
    if 'Time' not in df.columns or 'IWV' not in df.columns:
        raise ValueError(f"El fichero {csv_file} debe contener columnas 'Time' e 'IWV'.")

    # Seleccionar solo una de cada 'period' muestras
    df = df.iloc[::period].reset_index(drop=True)

    times = pd.to_datetime(df['Time'])
    iwvs = df['IWV']

    opacities = []
    for iwv in iwvs:
        atm_output = run_atm_with_iwv_and_freq(iwv, freq, atm_input_template)
        opacity = extract_opacity(atm_output)
        opacities.append(opacity)

    return times, opacities

def plot_opacities(results, freq):
    """
    Dibuja una curva de opacidad para cada fichero para una frecuencia dada.
    """
    plt.figure(figsize=(12, 6))
    for label, (times, opacities) in results.items():
        plt.plot(times, opacities, label=label)
    plt.xlabel("Fecha")
    plt.ylabel("Opacidad atmosférica total")
    plt.title(f"Opacidad atmosférica calculada con ATM (freq = {freq} GHz)")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    os.makedirs(PLOTS_DIR, exist_ok=True)
    freq_str = str(freq).replace('.', 'p')
    plt.savefig(os.path.join(PLOTS_DIR, f"atm_opacity_{freq_str}.png"))
    plt.close()
    print(f"Gráfica guardada en {os.path.join(PLOTS_DIR, f'atm_opacity_{freq_str}.png')}")

def main():
    args = parse_args()
    freq_list = [float(f) for f in args.freq.split(",")]
    for freq in freq_list:
        results = {}
        for csv_file in args.files:
            print(f"Procesando {csv_file} para frecuencia {freq} GHz...")
            label = os.path.basename(csv_file)
            times, opacities = process_file(csv_file, ATM_INPUT_TEMPLATE, freq, period=args.period)
            results[label] = (times, opacities)
        plot_opacities(results, freq)

if __name__ == "__main__":
    main()


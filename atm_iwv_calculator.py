#!/usr/bin/python3

"""
Autor: Pablo H.
Fecha: 07/25

Descripción:
Este script contiene las funciones necesarias para realizar los calculos del IWV (Integrated Water Vapor) en los otros scripts.

Además, de ejecutarlo, se obtiene el valor del IWV actual empleando la formula.
"""

import math

# Formulas sacadas del código en Java del 40M #######################################################
def dew_temperature(temperatura_c:float, humedad_relativa:float):
    """
    Calcula el punto de rocío (en °C) usando la fórmula.
    """
    a = 17.62
    b = 243.12  # °C

    # Para evitar problemas con el 0
    if humedad_relativa < 0.01:
        humedad_relativa = 0.01

    if humedad_relativa < 0 or humedad_relativa > 100:
        raise ValueError("La humedad relativa debe estar entre 0 y 100%.")

    alpha = ((a * temperatura_c) / (b + temperatura_c)) + math.log(humedad_relativa / 100.0)
    punto_rocio = (b * alpha) / (a - alpha)
    return punto_rocio

def calc_iwv_wh2o(surface_temp: float, humedad_relativa: float, scale_factor_H: float):
    """
    Calcula el IWV usando el punto de rocío.
    """
    mh2o = 1.66053886e-27 * 18
    kb = 1.3806503e-23

    # Dew temperature
    tdew = dew_temperature(surface_temp, humedad_relativa)

    # Partial pressure of water vapor (mb)
    ph2ombar = math.exp(1.81 + 17.27 * tdew / (tdew + 237.15))
    ph2o = ph2ombar * 100  # Pa

    # Temperatura en kelvin
    tk = surface_temp + 273.15

    # resultado
    wh2omm = mh2o * ph2o * scale_factor_H / (kb * tk)
    return wh2omm
# Fin de las formulas del 40M ##################################################################

def calc_iwv(surface_temp: float, scale_factor_H: float, humidity: float):
    """
    Calcula el IWV a partir de temperatura superficial, factor de escala y humedad relativa.
    """
    numerador = math.exp(17.27 * surface_temp / (surface_temp + 237.7))
    iwv = 1.3227e-2 * ((numerador) / (surface_temp + 273)) * humidity * scale_factor_H
    return iwv

def clean_value(val, unit):
    """
    Limpia el valor numérico de una cadena con unidad.
    """
    return float(val.replace(unit, '').replace(',', '.').strip())

def main():
    return

if __name__ == "__main__":
    main()

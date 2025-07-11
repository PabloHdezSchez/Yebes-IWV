# Scripts para Procesamiento y Análisis de IWV en el Observatorio de Yebes

Este repositorio contiene herramientas para la descarga, procesamiento, análisis y visualización de datos de IWV (Integrated Water Vapor) obtenidos en el Observatorio de Yebes a partir de estaciones GNSS y sensores meteorológicos.

## Scripts incluidos

### 1. `get_gss_csv.py`

- **Función:** Descarga archivos de IWV desde el portal del IGN, los convierte a formato CSV y los guarda en el directorio `./data`.
- **Funcionamiento:**
  - Descarga los archivos de texto especificados.
  - Convierte cada archivo a CSV con columnas `fecha` y `valor`.
  - Elimina el archivo TXT original tras la conversión.
- **Uso:**  
  Ejecuta el script directamente. Los archivos descargados estarán en `./data`.

---

### 2. `gnss_graphs.py`

- **Función:** Procesa y grafica los valores de IWV de varias estaciones GNSS.
- **Funcionamiento:**
  - Lee uno o más archivos CSV de IWV (cada uno de una estación).
  - Permite filtrar por año y ajustar la ventana de media móvil centrada.
  - Grafica los valores originales y la media móvil para cada estación.
  - Calcula y grafica una serie combinada promediando los valores de todas las estaciones.
  - Guarda las gráficas generadas en formato PNG.
- **Uso:**  
  ```bash
  python3 representation.py -y YEAR -w WINDOW -f file1.csv file2.csv ...
  ```
  - `-y YEAR`: Año a analizar (opcional, por defecto el actual).
  - `-w WINDOW`: Tamaño de la ventana para la media móvil (opcional).
  - `-f`: Lista de archivos CSV de entrada.

---

### 3. `iwv_graphs.py`

- **Función:** Calcula y representa el IWV a partir de archivos de humedad y temperatura, y lo compara con los datos de referencia.
- **Funcionamiento:**
  - Lee archivos CSV de humedad y temperatura, limpia y convierte los valores.
  - Une los datos por fecha/hora.
  - Calcula el IWV aplicando la fórmula.
  - Lee el archivo de referencia `Avg_data.csv` y lo representa junto a los IWV calculados.
  - Grafica los errores absolutos entre los métodos y el dato de referencia.
- **Uso:**  
  ```bash
  python3 iwv_calc.py -y YEAR -hf H_FACTOR
  ```
  - `-y YEAR`: Año de los datos a analizar.
  - `-hf H_FACTOR`: Factor de escala H para el cálculo de IWV.

---

## Requisitos

- Python 3.x
- Paquetes: `pandas`, `matplotlib`, `wget` (y otros estándar)

## Estructura de datos esperada

- Archivos CSV de IWV: columnas `fecha` (YYYY-MM-DD HH:MM:SS) e `IWV` (mm)
- Archivos de humedad: columnas `"Time","Humedad Relativa"`
- Archivos de temperatura: columnas `"Time","Temperatura"`

---

## Contacto

Para dudas o mejoras, contactar con Pablo H.

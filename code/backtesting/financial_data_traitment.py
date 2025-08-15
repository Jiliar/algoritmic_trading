import pandas as pd
import json
import os

"""
Módulo para tratamiento de datos financieros: extracción de PDH/PDL únicos y guardado de logs.
"""

import os
import pandas as pd

def obtener_datos_pdh_pdl_unicos(file_path):
    """
    Lee un archivo CSV y extrae los valores únicos de PDH y PDL por fecha,
    almacenándolos en un solo diccionario.
    
    Parámetros:
    ----------
    file_path : str
        Ruta al archivo CSV.

    Retorna:
    -------
    dict
        Un diccionario con fechas y sus correspondientes valores de PDH y PDL.
    """
    try:
        df = pd.read_csv(file_path)

        # 1. Convierte la columna 'date' a datetime y luego a formato de fecha (YYYY-MM-DD)
        df['date'] = pd.to_datetime(df['date']).dt.date

        # 2. Elimina las filas con valores nulos en 'pdh' o 'pdl'
        df.dropna(subset=['pdh', 'pdl'], inplace=True)
        
        # 3. Elimina duplicados basándose en la fecha
        df.drop_duplicates(subset=['date'], keep='first', inplace=True)

        # 4. Crea el diccionario final
        unique_dict = {}
        for index, row in df.iterrows():
            date_str = str(row['date'])
            unique_dict[date_str] = {
                'pdh': row['pdh'],
                'pdl': row['pdl']
            }
        
        return unique_dict
    except Exception:
        return None

    except FileNotFoundError:
        print(f"Error: El archivo no se encontró en la ruta '{file_path}'.")
        return None
    except KeyError as e:
        print(f"Error: No se encontró la columna requerida en el archivo CSV: {e}")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return None


def obtener_fechas_unicas_del_csv(file_path):
    """
    Lee un archivo CSV, convierte la columna 'date' a formato de fecha
    y retorna una lista de todas las fechas únicas.

    Parámetros:
    ----------
    file_path : str
        Ruta al archivo CSV.

    Retorna:
    -------
    list
        Una lista de objetos datetime.date, cada uno representando una fecha única
        en el archivo.
    """
    try:
        # Lee el archivo CSV
        df = pd.read_csv(file_path)

        # 1. Convierte la columna 'date' a formato de fecha y hora
        df['date'] = pd.to_datetime(df['date'])

        # 2. Extrae solo la parte de la fecha y elimina duplicados
        fechas_unicas = df['date'].dt.date.unique()

        # 3. Convierte el array de numpy a una lista de Python
        return list(fechas_unicas)

    except FileNotFoundError:
        print(f"Error: El archivo no se encontró en la ruta '{file_path}'.")
        return None
    except KeyError:
        print("Error: El archivo CSV no contiene una columna llamada 'date'.")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return None

"""
Module to download financial data from Financial Modeling Prep (FMP)
and add calculated indicators like PDH, PDL, and wick information.
"""
import time
from datetime import datetime, timedelta

import pandas as pd
import os
from fmp_python.fmp import FMP


def download_data(api_key, start_date, end_date, timeframe, symbol, output_dir="."):
    """
    Download intraday historical data from FMP in 10-day chunks and save it to CSV.

    Parameters:
    ----------
    api_key : str
        Your FMP API key.
    start_date : str
        Start date in 'YYYY-MM-DD' format.
    end_date : str
        End date in 'YYYY-MM-DD' format.
    timeframe : str
        Timeframe for the data, e.g. '5min', '15min', '1hour'.
    symbol : str
        Financial instrument symbol, e.g. 'EURUSD'.
    output_dir : str
        Directory where the CSV file will be saved. Default is current directory.

    Returns:
    -------
    str
        Path to the saved CSV file.
    """
    # API connection
    fmp = FMP(api_key=api_key, output_format='pandas')

    # Date handling
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    all_dataframes = []
    current_dt = start_dt

    # Loop in 10-day chunks
    while current_dt <= end_dt:
        chunk_end_dt = min(current_dt + timedelta(days=9), end_dt)
        print(f"Downloading {symbol} data from {current_dt.date()} to {chunk_end_dt.date()}")

        df_chunk = fmp.get_historical_chart(timeframe, symbol)
        df_chunk['date'] = pd.to_datetime(df_chunk['date'])
        df_chunk = df_chunk[
            (df_chunk['date'] >= current_dt) &
            (df_chunk['date'] <= chunk_end_dt)
        ]

        all_dataframes.append(df_chunk)
        current_dt = chunk_end_dt + timedelta(days=1)
        time.sleep(1)

    df_final = pd.concat(all_dataframes).drop_duplicates().sort_values('date')
    file_name = f"{symbol}_{timeframe}_{start_dt.strftime('%Y%m%d')}_{end_dt.strftime('%Y%m%d')}.csv"
    file_path = f"{output_dir}/{file_name}"

    df_final.to_csv(file_path, index=False)
    print(f"File saved: {file_path}")
    print(f"Total records: {len(df_final)}")
    return file_path


def add_wick_info_to_csv(file_path):
    """
    Agrega columnas de upper_wick, lower_wick y total_wick al archivo CSV especificado.

    Parámetros:
    ----------
    file_path : str
        Ruta del archivo CSV a modificar.
    """
    df = pd.read_csv(file_path)
    df['upper_wick'] = df['high'] - df[['open', 'close']].max(axis=1)
    df['lower_wick'] = df[['open', 'close']].min(axis=1) - df['low']
    df['total_wick'] = df['upper_wick'] + df['lower_wick']
    df.to_csv(file_path, index=False)
    print(f"Columnas 'upper_wick', 'lower_wick' y 'total_wick' agregadas a {file_path}. Total de registros: {len(df)}")


def add_pdh_pdl_to_csv(file_path, target_date, output_file=None):
    """
    Agrega columnas 'pdh' y 'pdl' al CSV, asignando el mismo valor a todas las filas
    correspondientes a la fecha especificada.

    Parámetros:
    ----------
    file_path : str
        Ruta del archivo CSV a modificar.
    target_date : str
        Fecha objetivo en formato 'YYYY-MM-DD' para calcular PDH y PDL.
    output_file : str, opcional
        Ruta de archivo para guardar el resultado. Si es None, sobrescribe el archivo original.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: El archivo no se encontró en la ruta '{file_path}'.")
        return

    df['date'] = pd.to_datetime(df['date'])

    if df['date'].dt.tz is not None or df['date'].astype(str).str.contains(r'[+-][0-9]{2}:[0-9]{2}$').any():
        try:
            df['date'] = pd.to_datetime(df['date'], utc=True)
            df['date'] = df['date'].dt.tz_convert('America/Bogota')
        except Exception as e:
            print(f"Error al manejar la zona horaria: {e}")
            return

    mask = df['date'].dt.strftime('%Y-%m-%d') == target_date
    if not mask.any():
        print(f"No hay datos para la fecha {target_date}")
        return

    pdh_value = df.loc[mask, 'high'].max()
    pdl_value = df.loc[mask, 'low'].min()

    df.loc[mask, 'pdh'] = pdh_value
    df.loc[mask, 'pdl'] = pdl_value

    save_path = output_file if output_file else file_path
    df.to_csv(save_path, index=False)
    print(f"PDH ({pdh_value}) y PDL ({pdl_value}) agregados para la fecha {target_date}. Filas afectadas: {mask.sum()}")

def save_log_to_file(log_text, log_folder='logs', log_filename='output.log'):
    """
    Guarda el texto de log en un archivo plano, reemplazando el archivo anterior si existe.
    Crea la carpeta si no existe.
    """
    os.makedirs(log_folder, exist_ok=True)
    log_path = os.path.join(log_folder, log_filename)
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(log_text)
    print(f"Log guardado en: {log_path}")
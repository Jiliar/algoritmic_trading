import pandas as pd
import json
import os

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
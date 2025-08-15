from fmp_python.fmp import FMP
import pandas as pd
from datetime import datetime, timedelta
import time

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
        chunk_end_dt = current_dt + timedelta(days=9)
        if chunk_end_dt > end_dt:
            chunk_end_dt = end_dt

        print(f"Downloading {symbol} data from {current_dt.date()} to {chunk_end_dt.date()}")

        # FMP call (returns all available data for that timeframe)
        df_chunk = fmp.get_historical_chart(timeframe, symbol)

        # Convert to datetime and filter the current chunk
        df_chunk['date'] = pd.to_datetime(df_chunk['date'])
        df_chunk = df_chunk[
            (df_chunk['date'] >= current_dt) &
            (df_chunk['date'] <= chunk_end_dt)
        ]

        all_dataframes.append(df_chunk)

        # Move to next chunk
        current_dt = chunk_end_dt + timedelta(days=1)

        # Sleep to respect API limits
        time.sleep(1)

    # Merge and sort all chunks
    df_final = pd.concat(all_dataframes).drop_duplicates().sort_values('date')

    # File name format: SYMBOL_TIMEFRAME_YYYYMMDD_YYYYMMDD.csv
    file_name = f"{symbol}_{timeframe}_{start_dt.strftime('%Y%m%d')}_{end_dt.strftime('%Y%m%d')}.csv"
    file_path = f"{output_dir}/{file_name}"

    # Save to CSV
    df_final.to_csv(file_path, index=False)
    print(f"File saved: {file_path}")
    print(f"Total records: {len(df_final)}")

    return file_path


# función para agregar columnas de wick al CSV
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
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])

    # Si la columna 'date' tiene zona horaria, convertir a la zona local (America/Bogota)
    if df['date'].dt.tz is not None or df['date'].astype(str).str.contains(r'[+-][0-9]{2}:[0-9]{2}$').any():
        try:
            df['date'] = pd.to_datetime(df['date'], utc=True)
            df['date'] = df['date'].dt.tz_convert('America/Bogota')
        except Exception:
            pass

    # Buscar por la parte de fecha local ignorando la hora y el offset
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


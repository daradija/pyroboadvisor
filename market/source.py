import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

import os
import pickle
import hashlib
import functools
from concurrent.futures import ThreadPoolExecutor, as_completed

def make_hash(func_name, args, kwargs):
    """Crea un hash único para la función y sus argumentos."""
    data = (func_name, tuple(sorted(kwargs.items())))
    data_bytes = pickle.dumps(data)
    return hashlib.md5(data_bytes).hexdigest()

def disk_cache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Crear la carpeta de cache si no existe
        cache_dir = "../cache"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Crear el hash y el nombre del archivo
        key = make_hash(func.__name__, args, kwargs)
        cache_file = os.path.join(cache_dir, f"{key}.pkl")
        
        # Si el archivo ya existe, cargar el resultado
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                return pickle.load(f)
        
        # Si no, llamar a la función y guardar el resultado
        result = func(*args, **kwargs)
        with open(cache_file, "wb") as f:
            pickle.dump(result, f)
        return result

    return wrapper

class Source:
    LIMITES_INTERVALO = {
        "1m": 730,
        "2m": 730,
        "5m": 730,
        "15m": 730,
        "30m": 730,
        "1h": 730,
        "1d": None,
        "1wk": None,
        "1mo": None,
    }

    def __init__(self, lista_instrumentos, fecha_inicio, fecha_fin, intervalo):
        self.lista_instrumentos = lista_instrumentos
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.intervalo = intervalo
        self.datos_por_instrumento = {}

        gestor = self
        gestor.descargar_datos()
        datos_limpiados = gestor.limpiar_datos()
        # saca las claves en self.symbols
        self.symbols = list(datos_limpiados.keys())
        self.size= len(self.symbols)

        self.dates=[]
        self.open=[]
        self.close=[]
        self.high=[]
        self.low=[]
        for symbol in self.symbols:
            df = datos_limpiados[symbol]
            self.dates.append(df['Date'].tolist())
            self.open.append(df['Open'].tolist())
            self.close.append(df['Close'].tolist())
            self.high.append(df['High'].tolist())
            self.low.append(df['Low'].tolist())
        self.dates = self.dates
        self.open = self.open
        self.close = self.close
        self.high = self.high
        self.low = self.low
        


    def dividir_rango_fechas(self, inicio, fin, max_dias):
        bloques = []
        inicio_dt = datetime.strptime(inicio, "%Y-%m-%d")
        fin_dt = datetime.strptime(fin, "%Y-%m-%d")
        while inicio_dt < fin_dt:
            bloque_fin_dt = min(inicio_dt + timedelta(days=max_dias), fin_dt)
            bloques.append((inicio_dt.strftime("%Y-%m-%d"), bloque_fin_dt.strftime("%Y-%m-%d")))
            inicio_dt = bloque_fin_dt + timedelta(days=1)
        return bloques

    @disk_cache
    def get_datos(self,instrumento=None,start=None,end=None,interval=None,progress=False):
        return yf.download(
            instrumento,
            start=start,
            end=end,
            interval=interval,
            progress=progress
        )
    def descargar_datos(self):
        try:
            limite = self.LIMITES_INTERVALO.get(self.intervalo)
            bloques = self.dividir_rango_fechas(self.fecha_inicio, self.fecha_fin, limite) if limite else [(self.fecha_inicio, self.fecha_fin)]

            def fetch(instrumento, start, end):
                print(f"📥 Descargando {instrumento} desde {start} hasta {end} con intervalo {self.intervalo}")
                df = self.get_datos(
                    instrumento=instrumento,
                    start=start,
                    end=end,
                    interval=self.intervalo,
                    progress=False
                )
                if not df.empty:
                    df = self.aplanar_columnas(df)
                    df.reset_index(inplace=True)
                return (instrumento, start, end, df)

            tasks = []
            with ThreadPoolExecutor(max_workers=8) as executor:
                for instrumento in self.lista_instrumentos:
                    for start, end in bloques:
                        tasks.append(executor.submit(fetch, instrumento, start, end))

                symbol_data = {}
                for future in as_completed(tasks):
                    instrumento, start, end, df = future.result()
                    if df is not None and not df.empty:
                        symbol_data.setdefault(instrumento, []).append(df)
                    else:
                        print(f"⚠️ No se han obtenido datos para {instrumento} entre {start} y {end}")

            for instrumento, dfs in symbol_data.items():
                self.datos_por_instrumento[instrumento] = pd.concat(dfs, ignore_index=True)

            return self.datos_por_instrumento

        except Exception as error:
            print(f"❌ Error al descargar los datos: {error}")
            return None

    def aplanar_columnas(self, df):
        """
        Asegura que el DataFrame no tenga MultiIndex en las columnas.
        Si las columnas incluyen el nombre del activo (ej. 'Close AAPL'), se eliminan esas referencias.
        """
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [' '.join(col).strip() for col in df.columns.values]

        df.columns = [col.split(' ')[0] if ' ' in col else col for col in df.columns]
        return df

    def limpiar_datos(self):
        if self.datos_por_instrumento:
            for instrumento, df in self.datos_por_instrumento.items():
                df.dropna(inplace=True)
                df.drop_duplicates(inplace=True)
                self.datos_por_instrumento[instrumento] = df
            return self.datos_por_instrumento
        else:
            print("⚠️ No hay datos para limpiar.")
            return None

    def realTime(self,symbols):
        """
        Obtiene el precio casi “en vivo” de los instrumentos especificados.
        """
        resultados = []  # para devolver un dict {símbolo: precio}
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                # regularMarketPrice = último precio en la sesión regular
                precio = ticker.info.get("regularMarketPrice", None)
                if precio is None:
                    # fallback: usar la última vela (por si ticker.info falla)
                    hist = ticker.history(period="1d", interval=self.intervalo, prepost=True)
                    if not hist.empty:
                        precio = hist["Close"].iloc[-1]
                if precio is not None:
                    resultados.append(precio)
                    print(f"📈 {symbol} - Current price: {precio}")
                else:
                    resultados.append(0)
                    print(f"⚠️ No se obtuvo precio para {symbol}")
            except Exception as e:
                print(f"❌ Error para {symbol}: {e}")
                resultados[symbol] = None

        return resultados



if __name__ == "__main__":
    instrumentos = ["AAPL", "GOOGL"]
    fecha_inicio = "2023-01-01"
    fecha_fin = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    intervalo = "1d"

    Source(instrumentos, fecha_inicio, fecha_fin, intervalo)

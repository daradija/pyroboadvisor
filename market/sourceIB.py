import os
import pickle
import hashlib
import functools
from datetime import datetime

import pandas as pd

from driver.driverIB import DriverIB
from market.source import Source


def make_hash(func_name, args, kwargs):
    """Crea un hash único para la función y sus argumentos."""
    data = (func_name, tuple(sorted(kwargs.items())))
    data_bytes = pickle.dumps(data)
    return hashlib.md5(data_bytes).hexdigest()


def disk_cache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cache_dir = args[0].cache
        os.makedirs(cache_dir, exist_ok=True)
        key = make_hash(func.__name__, args, kwargs)
        cache_file = os.path.join(cache_dir, f"{key}.pkl")
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                return pickle.load(f)
        result = func(*args, **kwargs)
        with open(cache_file, "wb") as f:
            pickle.dump(result, f)
        return result

    return wrapper


class SourceIB(Source):
    """Implementación de la fuente de datos para TWS API de Interactive Brokers."""

    name = "Interactive Brokers"

    def __init__(self, p, cache, lista_instrumentos, fecha_inicio, fecha_fin, intervalo):
        self.cache = cache
        self.lista_instrumentos = lista_instrumentos
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.intervalo = intervalo
        self.datos_por_instrumento = {}
        self.p = p or {}

        self.port = int(self.p.get("ib_port", 7497))
        self.driver = DriverIB(self.port)
        self.driver.conectar(desatendido=bool(self.p.get("desatendido", False)))

        self.descargar_datos()
        datos_limpiados = self.limpiar_datos() or {}

        self.symbols = list(datos_limpiados.keys())
        self.size = len(self.symbols)

        self.dates = []
        self.open = []
        self.close = []
        self.high = []
        self.low = []

        for symbol in self.symbols:
            df = datos_limpiados[symbol]
            self.dates.append(df['Date'].tolist())
            self.open.append(df['Open'].tolist())
            self.close.append(df['Close'].tolist())
            self.high.append(df['High'].tolist())
            self.low.append(df['Low'].tolist())

    def _fetch_with_source_yahoo(self, instrumentos):
        from market.sourceYahoo import SourceYahoo
        source_yahoo = SourceYahoo(self.p, self.cache, instrumentos, self.fecha_inicio, self.fecha_fin, self.intervalo)
        return source_yahoo.datos_por_instrumento

    @disk_cache
    def _get_historical_data(self, instrumento, start, end, interval):
        datos = self._fetch_with_source_yahoo([instrumento])
        df = datos.get(instrumento, pd.DataFrame())
        if df.empty:
            return df

        if 'Date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['Date']):
            df['Date'] = pd.to_datetime(df['Date'])
        return df

    def descargar_datos(self):
        try:
            for instrumento in self.lista_instrumentos:
                print(f"📥 Solicitando datos IB para {instrumento} desde {self.fecha_inicio} hasta {self.fecha_fin} con intervalo {self.intervalo}")
                df = self._get_historical_data(
                    instrumento=instrumento,
                    start=self.fecha_inicio,
                    end=self.fecha_fin,
                    interval=self.intervalo,
                )
                if df.empty:
                    print(f"⚠️ No se han obtenido datos para {instrumento} desde IB.")
                else:
                    self.datos_por_instrumento[instrumento] = df
            return self.datos_por_instrumento
        except Exception as error:
            print(f"❌ Error al descargar los datos de IB: {error}")
            return None

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

    def _build_contracts(self, symbols):
        return [self.driver.createContract(symbol) for symbol in symbols]

    def _extract_price(self, ticker):
        for attr in ('marketPrice', 'last', 'close'):
            precio = getattr(ticker, attr, None)
            if precio is not None:
                return precio
        return None

    def _request_batch_tickers(self, contracts):
        try:
            tickers = self.driver.ib.reqTickers(*contracts)
            self.driver.ib.sleep(1)
            return tickers
        except Exception:
            return None

    def realTime(self, symbols):
        resultados = []
        contracts = self._build_contracts(symbols)
        tickers = self._request_batch_tickers(contracts)

        if tickers is not None:
            prices = {ticker.contract.symbol: self._extract_price(ticker) for ticker in tickers}
            for symbol in symbols:
                precio = prices.get(symbol)
                if precio is not None:
                    resultados.append(precio)
                    print(f"📈 {symbol} - Current IB price: {precio}")
                else:
                    resultados.append(0)
                    print(f"⚠️ No se obtuvo precio para {symbol} desde IB")
            return resultados

        for symbol in symbols:
            try:
                contract = self.driver.createContract(symbol)
                tickers = self.driver.ib.reqTickers(contract)
                self.driver.ib.sleep(1)

                if not tickers:
                    resultados.append(0)
                    print(f"⚠️ No se obtuvo precio para {symbol} desde IB")
                    continue

                ticker = tickers[0]
                precio = self._extract_price(ticker)

                if precio is not None:
                    resultados.append(precio)
                    print(f"📈 {symbol} - Current IB price: {precio}")
                else:
                    resultados.append(0)
                    print(f"⚠️ No se obtuvo precio para {symbol} desde IB")
            except Exception as e:
                print(f"❌ Error IB para {symbol}: {e}")
                resultados.append(0)

        return resultados

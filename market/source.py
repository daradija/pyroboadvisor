import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

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
        return datos_limpiados

    def dividir_rango_fechas(self, inicio, fin, max_dias):
        bloques = []
        inicio_dt = datetime.strptime(inicio, "%Y-%m-%d")
        fin_dt = datetime.strptime(fin, "%Y-%m-%d")
        while inicio_dt < fin_dt:
            bloque_fin_dt = min(inicio_dt + timedelta(days=max_dias), fin_dt)
            bloques.append((inicio_dt.strftime("%Y-%m-%d"), bloque_fin_dt.strftime("%Y-%m-%d")))
            inicio_dt = bloque_fin_dt + timedelta(days=1)
        return bloques

    def descargar_datos(self):
        try:
            limite = self.LIMITES_INTERVALO.get(self.intervalo)
            if limite is not None:
                bloques = self.dividir_rango_fechas(self.fecha_inicio, self.fecha_fin, limite)
            else:
                bloques = [(self.fecha_inicio, self.fecha_fin)]
            
            for instrumento in self.lista_instrumentos:
                lista_dfs = []
                for bloque in bloques:
                    inicio_bloque, fin_bloque = bloque
                    print(f"📥 Descargando {instrumento} desde {inicio_bloque} hasta {fin_bloque} con intervalo {self.intervalo}")
                    df_bloque = yf.download(
                        instrumento,
                        start=inicio_bloque,
                        end=fin_bloque,
                        interval=self.intervalo,
                        progress=False
                    )
                    if not df_bloque.empty:
                        df_bloque = self.aplanar_columnas(df_bloque)
                        df_bloque.reset_index(inplace=True)
                        lista_dfs.append(df_bloque)
                
                if lista_dfs:
                    self.datos_por_instrumento[instrumento] = pd.concat(lista_dfs, ignore_index=True)
                else:
                    print(f"⚠️ No se han obtenido datos para {instrumento} en el rango especificado.")
            
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



if __name__ == "__main__":
    instrumentos = ["AAPL", "GOOGL"]
    fecha_inicio = "2023-01-01"
    fecha_fin = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    intervalo = "1d"

    Source(instrumentos, fecha_inicio, fecha_fin, intervalo)

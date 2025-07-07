from datetime import datetime, date, timedelta
import pandas as pd
# Al inicio de evaluacion.py, agregar:
import matplotlib
matplotlib.use('Agg')  # Backend sin display
import matplotlib.pyplot as plt

class EstrategiaValuacionConSP500:
    def __init__(self, sp500_ticker='^GSPC', lookback_days=7):
        """
        Clase para almacenar valoración de estrategia y comparar con S&P 500.
        - add: almacena fechas y valores de estrategia solo.
        - print: al llamar, obtiene la serie de S&P 500 en el rango abarcado y escala.
        """
        self.fechas = []
        self.valores_estrategia = []
        self.sp500_ticker = sp500_ticker
        self.lookback_days = lookback_days
        try:
            import yfinance as yf
            self._yf = yf
        except ImportError:
            self._yf = None

    def _parse_fecha(self, fecha):
        if isinstance(fecha, str):
            try:
                return datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Formato de fecha inválido. Use 'YYYY-MM-DD'.")
        elif isinstance(fecha, datetime):
            return fecha.date()
        elif isinstance(fecha, date):
            return fecha
        else:
            raise ValueError("fecha debe ser str 'YYYY-MM-DD' o datetime.date/datetime.datetime")

    def add(self, fecha, valor_estrategia):
        """
        Añade fecha y valor de estrategia.
        No se obtiene SP500 aquí para eficiencia.
        """
        if valor_estrategia is None:
            return 
        fecha_dt = self._parse_fecha(fecha)
        self.fechas.append(fecha_dt)
        self.valores_estrategia.append(float(valor_estrategia))

    def print(self):
        """
        Dibuja la serie de estrategia y la del S&P 500 escalada.
        Obtiene la cotización del S&P 500 en el rango de fechas usadas.
        """
        if not self.fechas:
            print("No hay datos de estrategia para mostrar.")
            return

        # Ordenar por fecha
        datos = list(zip(self.fechas, self.valores_estrategia))
        datos_ordenados = sorted(datos, key=lambda x: x[0])
        fechas_ord, valores_ord = zip(*datos_ordenados)
        fechas_ord = list(fechas_ord)
        valores_ord = list(valores_ord)

        # Intentar obtener datos de SP500
        if self._yf is None:
            print("yfinance no está disponible; no se puede obtener SP500 automáticamente.")
            print("Solo se mostrará la serie de estrategia.")
            plt.figure()
            plt.plot(fechas_ord, valores_ord, label='Estrategia')
            plt.xlabel('Fecha')
            plt.ylabel('Valor')
            plt.title('Valoración diaria de la estrategia')
            plt.grid(True)
            plt.tight_layout()
            plt.show()
            return

        # Definir rango de fechas para descarga
        min_fecha = min(fechas_ord)
        max_fecha = max(fechas_ord)
        start_date = min_fecha - timedelta(days=self.lookback_days)
        end_date = max_fecha + timedelta(days=1)

        # Descargar datos
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        try:
            data = self._yf.download(self.sp500_ticker, start=start_str, end=end_str, progress=False)
        except Exception as e:
            print(f"Error descargando S&P 500: {e}. Solo se mostrará la serie de estrategia.")
            plt.figure()
            plt.plot(fechas_ord, valores_ord, label='Estrategia')
            plt.xlabel('Fecha')
            plt.ylabel('Valor')
            plt.title('Valoración diaria de la estrategia')
            plt.grid(True)
            plt.tight_layout()
            plt.show()
            return

        if data.empty:
            print(f"No se encontró cotización de {self.sp500_ticker} en el rango {start_str} a {end_str}.")
            print("Solo se mostrará la serie de estrategia.")
            plt.figure()
            plt.plot(fechas_ord, valores_ord, label='Estrategia')
            plt.xlabel('Fecha')
            plt.ylabel('Valor')
            plt.title('Valoración diaria de la estrategia')
            plt.grid(True)
            plt.tight_layout()
            plt.show()
            return

        # Preparar índice de fechas
        if hasattr(data.index, 'tz'):
            try:
                data.index = data.index.tz_localize(None)
            except Exception:
                pass
        data['date_only'] = data.index.normalize()
        # Construir lista de cotizaciones para cada fecha de estrategia
        sp500_raw_list = []
        for fecha in fechas_ord:
            # Filtrar precios con date_only <= fecha
            mask = data['date_only'] <= pd.Timestamp(fecha)
            sub = data.loc[mask]
            if sub.empty:
                raise RuntimeError(
                    f"No hay cotización válida del S&P 500 dentro de {self.lookback_days} días antes de {fecha}."
                    " Usa otro rango o añade manualmente."
                )
            ultima = sub.iloc[-1]
            fecha_usada = ultima.name.date()
            #precio = float(ultima['Adj Close'] if 'Adj Close' in data.columns else ultima['Close'])
            precio = float(ultima['Adj Close'].iloc[0] if 'Adj Close' in data.columns else ultima['Close'].iloc[0])
            if fecha_usada != fecha:
                print(f"Advertencia: para {fecha}, usando cotización SP500 de {fecha_usada}.")
            sp500_raw_list.append(precio)

        # Calcular factor y serie escalada
        sp500_primero = sp500_raw_list[0]
        if sp500_primero == 0:
            raise ValueError("Cotización SP500 en fecha inicial es cero; no se puede escalar.")
        factor = valores_ord[0] / sp500_primero
        sp500_escalada = [v * factor for v in sp500_raw_list]

        # Graficar ambas series
        plt.figure()
        plt.plot(fechas_ord, valores_ord, label='Estrategia A1')
        plt.plot(fechas_ord, sp500_escalada, label='S&P 500 escalado', linestyle='--')
        plt.xlabel('Fecha')
        plt.ylabel('Valor')
        plt.title('Comparativa: Estrategia vs S&P 500 (escalado)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()


from datetime import datetime, date, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
from matplotlib.colors import LinearSegmentedColormap  # <-- NUEVO IMPORT

class SharpeLog:
    def __init__(self):
        # Para la media
        self.sx = 0
        self.n = 0
        # Para la desviación estándar
        self.s2x = 0
        self.previusX = None

    def add(self, x):
        if self.previusX is not None:
            rlog = math.log(x / self.previusX)
            self.sx += rlog
            self.s2x += rlog * rlog
            self.n += 1
        self.previusX = x

    def sharpeLog(self):
        # media dividido por desviación
        if self.n == 0:
            return 0.0
        denominador = self.n * math.sqrt(self.s2x / self.n)
        if denominador == 0:
            return 0.0
        return self.sx / denominador * 252 / math.sqrt(252)  # Anualizado, asumiendo 252 días de trading al año


class EstrategiaValuacionConSP500:
    def __init__(self, sp500_ticker='^GSPC', lookback_days=7):
        """
        Clase para almacenar valoración de estrategia y comparar con S&P 500.
        - add: almacena fechas y valores de estrategia solo.
        - print: al llamar, obtiene la serie de S&P 500 en el rango abarcado y escala.
        """
        self.fechas = []
        self.valores_estrategia = []
        # nueva serie de retornos logarítmicos diarios de la estrategia
        self.returns_estrategia = []

        self.sp500_ticker = sp500_ticker
        self.lookback_days = lookback_days
        self.sharpe_log = SharpeLog()
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
        Además, calcula y guarda el retorno logarítmico diario.
        """
        if valor_estrategia is None:
            return

        # Sharpe log incremental
        self.sharpe_log.add(valor_estrategia)
        print(f"Sharpe Log (A/SP500): {self.sharpe_log.sharpeLog()/0.59:.2f}")  # 0.59 es el Sharpe Log del SP500

        fecha_dt = self._parse_fecha(fecha)

        # Cálculo de retorno logarítmico diario de la estrategia
        if self.valores_estrategia:
            prev_valor = self.valores_estrategia[-1]
            if prev_valor is not None and prev_valor > 0:
                r_log = math.log(float(valor_estrategia) / float(prev_valor))
                self.returns_estrategia.append(r_log)
            else:
                self.returns_estrategia.append(None)
        else:
            # primer día no tiene retorno definido
            self.returns_estrategia.append(None)

        self.fechas.append(fecha_dt)
        self.valores_estrategia.append(float(valor_estrategia))

    def print(self, strategy_name):
        """
        Dibuja la serie de estrategia y la del S&P 500 escalada.
        Obtiene la cotización del S&P 500 en el rango de fechas usadas.
        Luego:
          1) Gráfico Estrategia vs S&P500 escalado
          2) Dispersión de rentabilidades logarítmicas (ya existente)
          3) Heatmap mensual/anual de rentabilidades de la estrategia (nuevo)
        """
        if not self.fechas:
            print("No hay datos de estrategia para mostrar.")
            return

        # Ordenar por fecha, manteniendo también los retornos sincronizados
        datos = list(zip(self.fechas, self.valores_estrategia, self.returns_estrategia))
        datos_ordenados = sorted(datos, key=lambda x: x[0])
        fechas_ord, valores_ord, returns_ord = map(list, zip(*datos_ordenados))
        fechas_ord = list(fechas_ord)
        valores_ord = list(valores_ord)
        returns_ord = list(returns_ord)

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
            precio = float(ultima['Adj Close'] if 'Adj Close' in data.columns else ultima['Close'])
            if fecha_usada != fecha:
                print(f"Advertencia: para {fecha}, usando cotización SP500 de {fecha_usada}.")
            sp500_raw_list.append(precio)

        # Calcular factor y serie escalada
        sp500_primero = sp500_raw_list[0]
        if sp500_primero == 0:
            raise ValueError("Cotización SP500 en fecha inicial es cero; no se puede escalar.")
        factor = valores_ord[0] / sp500_primero
        sp500_escalada = [v * factor for v in sp500_raw_list]

        # 1) Graficar ambas series
        plt.figure()
        plt.plot(fechas_ord, valores_ord, label='Estrategia ' + strategy_name)
        plt.plot(fechas_ord, sp500_escalada, label='S&P 500 escalado', linestyle='--')
        plt.xlabel('Fecha')
        plt.ylabel('Valor')
        plt.title('Comparativa: Estrategia vs S&P 500 (escalado)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # 2) Dispersión estrategia vs S&P500
        self.dotComparativo(valores_ord, sp500_raw_list, strategy_name)

        # 3) Heatmap mensual / anual de rentabilidades
        self.plot_heatmap_mensual_anual(fechas_ord, returns_ord, strategy_name)

        # 4) Histograma de rentabilidades diarias
        self.plot_hist_retornos(strategy_name)

    def dotComparativo(self, valores_estrategia, sp500_raw_list, strategy_name):
        # cacula rentabilidad logaritmica
        valores_estrategia_log = np.array([math.log(v) for v in valores_estrategia])
        sp500_raw_list_log = np.array([math.log(v) for v in sp500_raw_list])

        # Pasa a rentabilidad logaritmica
        valores_r_log = np.diff(valores_estrategia_log)
        sp500_r_log = np.diff(sp500_raw_list_log)

        # muestra grafica de dispersión
        plt.figure()
        plt.scatter(sp500_r_log, valores_r_log, alpha=0.5)
        plt.xlabel('Rentabilidad logarítmica S&P 500')
        plt.ylabel('Rentabilidad logarítmica Estrategia')
        plt.title(f'Dispersión: Estrategia "{strategy_name}" vs S&P 500')
        plt.grid(True)
        # Regresión lineal
        m, b = np.polyfit(sp500_r_log, valores_r_log, 1)
        plt.plot(sp500_r_log, m * sp500_r_log + b, color='red', linestyle='--', label='Regresión lineal')
        # Calcular y mostrar coeficiente de correlación
        correlation = np.corrcoef(sp500_r_log, valores_r_log)[0, 1]
        plt.text(
            0.05,
            0.90,
            f'Correlación: {correlation:.2f}',
            transform=plt.gca().transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(facecolor='white', alpha=0.5),
        )
        # Calcular y mostrar la ecuación de la recta
        plt.text(
            0.05,
            1,
            f'y = {m:.4f}x + {b:.4f}',
            transform=plt.gca().transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(facecolor='white', alpha=0.5),
        )
        # Mostrar leyenda y ajustar layout
        plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
        plt.axvline(0, color='black', linewidth=0.8, linestyle='--')
        plt.legend()
        plt.tight_layout()
        plt.show()
        print()

    def plot_heatmap_mensual_anual(self, fechas, returns_log, strategy_name):
        """
        Construye un heatmap año x mes con la rentabilidad mensual de la estrategia.
        - Usa retornos logarítmicos diarios: suma por mes y pasa a retorno simple.
        """
        # Empaquetar fechas y retornos, saltando None (primer día u otros casos)
        datos = [
            (pd.Timestamp(f), r)
            for f, r in zip(fechas, returns_log)
            if r is not None
        ]

        if not datos:
            print("No hay retornos suficientes para el heatmap mensual/anual.")
            return

        df = pd.DataFrame(datos, columns=["date", "r_log"])
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month

        # Suma de retornos logarítmicos por año/mes
        grouped = df.groupby(["year", "month"])["r_log"].sum().reset_index()
        # Pasar a retorno simple mensual
        grouped["ret"] = np.exp(grouped["r_log"]) - 1.0

        # Tabla año x mes
        pivot = grouped.pivot(index="year", columns="month", values="ret").sort_index()
        # Asegurar columnas 1..12 en orden
        all_months = list(range(1, 13))
        pivot = pivot.reindex(columns=all_months)

        # Si no hay nada, salir
        if pivot.empty:
            print("No se pudo construir el heatmap de rentabilidades mensuales.")
            return

        # Para pintar: matriz de datos y máscaras de NaN
        mask_nan = pivot.isna()
        pivot_filled = pivot.fillna(0.0)
        data_matrix = pivot_filled.values

        years = list(pivot.index)
        months = list(pivot.columns)

        month_labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

        plt.figure()

        # Rango de colores: de -50% a +50%
        vmin, vmax = -0.5, 0.5

        # Función para mapear un valor del rango [vmin, vmax] a [0, 1]
        def pos(x):
            return (x - vmin) / (vmax - vmin)

        # Colormap personalizado con tus colores:
        # -50%  -> #ff5b5b
        #  -5%  -> #ff8a5b
        #   0%  -> #ffffff
        #  +5%  -> #00ff6a
        # +50%  -> #00953e
        cmap = LinearSegmentedColormap.from_list(
            "custom_ret",
            [
                (0.0,        "#ff5b5b"),  # -50% o peor
                (pos(-0.05), "#fff0cd"),  # -5%
                (pos(0.0),   "#ffffff"),  # 0%
                (pos(0.05),  "#00ff6a"),  # +5%
                (1.0,        "#00953e"),  # +50% o más
            ]
        )

        im = plt.imshow(
            data_matrix,
            aspect="auto",
            interpolation="nearest",
            cmap=cmap,
            origin="lower",
            vmin=vmin,
            vmax=vmax,
        )
        plt.colorbar(im, label="Rentabilidad mensual")

        plt.xticks(
            ticks=range(len(months)),
            labels=[month_labels[m - 1] for m in months],
            rotation=0,
        )
        plt.yticks(
            ticks=range(len(years)),
            labels=years,
        )
        plt.xlabel("Mes")
        plt.ylabel("Año")
        plt.title(f"Heatmap mensual/anual de rentabilidades - {strategy_name}")

        # Anotar cada celda con la rentabilidad en %
        for i, year in enumerate(years):
            for j, month in enumerate(months):
                if mask_nan.iloc[i, j]:
                    continue
                val = data_matrix[i, j]
                plt.text(
                    j,
                    i,
                    f"{val * 100:.1f}%",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="black",
                )

        plt.tight_layout()
        plt.show()

    def plot_hist_retornos(self, strategy_name):
        """
        Histograma de rentabilidades logarítmicas diarias de la estrategia.
        Eje X: rentabilidad logarítmica diaria (%)
        Eje Y: porcentaje de días.
        """
        datos = [r for r in self.returns_estrategia if r is not None]
        if not datos:
            print("No hay retornos diarios suficientes para el histograma.")
            return

        # r_log diarios
        arr = np.array(datos)
        arr_pct = arr * 100.0  # para mostrar en "% logarítmico" en el eje X

        plt.figure()

        # Pesos para que el eje Y sea porcentaje de días
        weights = np.ones_like(arr_pct) / len(arr_pct)

        # Histograma: y = fracción de días en cada bin
        n, bins, patches = plt.hist(arr_pct, bins=50, weights=weights, alpha=0.9)

        # --- Colores consistentes con el heatmap pero en escala logarítmica ---
        # Tramos de referencia en rentabilidad SIMPLE:
        #  -50%  -> log(0.5)
        #   -5%  -> log(0.95)
        #    0%  -> log(1.0) = 0
        #   +5%  -> log(1.05)
        #  +50%  -> log(1.5)
        vmin = math.log(0.5)   # ~ -0.6931
        vmax = math.log(1.5)   # ~  0.4055

        def pos(x):
            return (x - vmin) / (vmax - vmin)

        cmap = LinearSegmentedColormap.from_list(
            "custom_ret",
            [
                (0.0,                     "#ff5b5b"),  # -50% o peor
                (pos(math.log(0.95)),     "#fff0cd"),  # -5%
                (pos(0.0),                "#eeeeeeee"),  # 0%
                (pos(math.log(1.05)),     "#00ff6a"),  # +5%
                (1.0,                     "#00953e"),  # +50% o más
            ]
        )

        # Colorear cada barra según el centro del bin en r_log
        for patch, left, right in zip(patches, bins[:-1], bins[1:]):
            center_pct = (left + right) / 2.0       # centro en "% log"
            center_log = center_pct / 100.0         # vuelve a escala log
            t = (center_log - vmin) / (vmax - vmin)
            t = min(1.0, max(0.0, t))               # recorte a [0,1]
            patch.set_facecolor(cmap(t))

        # --- Líneas de referencia ---
        # 0% logarítmico
        plt.axvline(0, color="black", linewidth=1, linestyle="--", label="0% log")

        # Media de las rentabilidades logarítmicas (en escala log)
        mean_log = arr.mean()
        mean_log_pct = mean_log * 100.0
        plt.axvline(
            mean_log_pct,
            color="red",
            linewidth=1,
            linestyle="-",
            label=f"Media {mean_log_pct:.3f}%",
        )

        # Escala vertical proporcional al máximo (en porcentaje de días)
        ax = plt.gca()
        ymax = max(n) * 1.05 if len(n) > 0 else 1.0
        ax.set_ylim(0, ymax)
        # Convertir ticks de fracción a porcentaje
        yticks = ax.get_yticks()
        ax.set_yticklabels([f"{yt*100:.1f}%" for yt in yticks])

        plt.xlabel("Rentabilidad logarítmica diaria (%)")
        plt.ylabel("Porcentaje de días")
        plt.title(f"Distribución de rentabilidades logarítmicas diarias - {strategy_name}")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()

from datetime import datetime, date, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import math
import numpy as np
from matplotlib.colors import LinearSegmentedColormap  # <-- NUEVO IMPORT

"""
=======================================
Estructura
=======================================

CLASE PRINCIPAL: SharpeLog (Cálculo incremental del ratio de Sharpe)
│
├── [INIT] __init__()
│   └── INIT[1.] CONFIGURACIÓN: Inicializar todas las variables acumuladoras
│
├── [ADD] add(x)
│   ├── ADD[1.] VERIFICACIÓN: Comprobar si hay valor anterior
│   ├── ADD[2.] CÁLCULO: Calcular retorno logarítmico
│   ├── ADD[3.] ACTUALIZACIÓN: Acumular estadísticas
│   └── ADD[4.] ALMACENAMIENTO: Guardar valor actual
│
└── [SHARPE] sharpeLog()
    ├── SHARPE[1.] VALIDACIÓN: Verificar datos suficientes
    ├── SHARPE[2.] CÁLCULO: Calcular desviación estándar
    ├── SHARPE[3.] VALIDACIÓN: Evitar división por cero
    ├── SHARPE[4.] CÁLCULO: Ratio de Sharpe diario
    └── SHARPE[5.] ANUALIZACIÓN: Convertir a base anual


CLASE PRINCIPAL: EstrategiaValuacionConSP500 (Sistema completo de análisis)
│
├── [INIT] __init__(sp500_ticker='^GSPC', lookback_days=7)
│   ├── INIT[1.] ALMACENAMIENTO: Inicializar listas para datos de estrategia
│   ├── INIT[2.] CONFIGURACIÓN: Establecer parámetros de comparación
│   ├── INIT[3.] MÉTRICAS: Configurar calculadora de Sharpe
│   └── INIT[4.] DEPENDENCIAS: Verificar disponibilidad de yfinance
│
├── [PARSE] _parse_fecha(fecha)
│   ├── PARSE[1.] STRING: Convertir cadena 'YYYY-MM-DD' a date
│   ├── PARSE[2.] DATETIME: Extraer date de objeto datetime
│   ├── PARSE[3.] DATE: Devolver directamente si ya es date
│   └── PARSE[4.] ERROR: Lanzar excepción para formato no soportado
│
├── [ADD] add(fecha, valor_estrategia)
│   ├── ADD[1.] VALIDACIÓN: Verificar valor no nulo
│   ├── ADD[2.] SHARPE: Actualizar ratio de Sharpe incremental
│   ├── ADD[3.] CONVERSIÓN: Normalizar formato de fecha
│   ├── ADD[4.] RETORNO: Calcular retorno logarítmico diario
│   └── ADD[5.] ALMACENAMIENTO: Guardar fecha y valor
│
├── [PRINT] print(strategy_name) - GENERA 6 GRÁFICOS DE ANÁLISIS
│   ├── print[1.] VALIDACIÓN INICIAL: Comprobar si hay datos de estrategia
│   ├── print[2.] ORDENACIÓN Y PREPARACIÓN DE DATOS DE ESTRATEGIA
│   ├── print[3.] VERIFICACIÓN DE DISPONIBILIDAD DE YFINANCE
│   ├── print[4.] DEFINICIÓN DEL RANGO DE FECHAS PARA DESCARGAR DATOS DEL S&P 500
│   ├── print[5.] DESCARGA DE DATOS HISTÓRICOS DEL S&P 500
│   ├── print[6.] VALIDACIÓN DE DATOS DESCARGADOS DEL S&P 500
│   ├── print[7.] PREPROCESAMIENTO DE DATOS DEL S&P 500
│   ├── print[8.] CONSTRUCCIÓN DE LA SERIE DE PRECIOS DEL S&P 500 SINCRONIZADA
│   ├── print[9.] ESCALADO DEL S&P 500 PARA COMPARACIÓN VISUAL
│   └── print[10.] GENERACIÓN DE LOS 6 GRÁFICOS DE ANÁLISIS:
│       ├── print[10.1] Gráfico 1: Comparativa en escala lineal (plot_series con log=False)
│       ├── print[10.2] Gráfico 2: Comparativa en escala logarítmica (plot_series con log=True)
│       ├── print[10.3] Gráfico 3: Dispersión de retornos diarios (dotComparativo)
│       ├── print[10.4] Gráfico 4: Heatmap de rentabilidades mensuales simples (plot_heatmap_mensual_anual con log=False)
│       ├── print[10.5] Gráfico 5: Heatmap de rentabilidades mensuales logarítmicas (plot_heatmap_mensual_anual con log=True)
│       └── print[10.6] Gráfico 6: Histograma de distribución de retornos diarios (plot_hist_retornos)
│
├── [UTIL] _get_unified_colormap(vmin, vmax)
│   └── Función auxiliar: Crea colormap unificado con colores fijos
│
├── [VIS-1] plot_series(fechas_ord, valores_ord, sp500_escalada, strategy_name, *, log=False)
│   ├── plot_series[1.] INICIALIZACIÓN: Crear nueva figura
│   ├── plot_series[2.] TRAZADO: Dibujar las dos series temporales
│   ├── plot_series[3.] CONFIGURACIÓN DE ESCALA: Lineal vs Logarítmica
│   └── plot_series[4.] CONFIGURACIÓN FINAL: Etiquetas y presentación
│
├── [VIS-2] dotComparativo(valores_estrategia, sp500_raw_list, strategy_name)
│   ├── Calcula rentabilidades logarítmicas de estrategia y S&P 500
│   ├── Crea gráfico de dispersión con regresión lineal
│   ├── Muestra coeficiente de correlación y ecuación de la recta
│   └── Añade líneas de referencia en 0% y leyenda
│
├── [VIS-3] plot_heatmap_mensual_anual(fechas, returns, strategy_name, *, log=False)
│   ├── heatmap[1.] PREPARACIÓN: Filtrar y estructurar datos
│   ├── heatmap[2.] AGRUPACIÓN: Calcular rentabilidades mensuales
│   ├── heatmap[3.] CONFIGURACIÓN: Definir parámetros según modo (log/simple)
│   ├── heatmap[4.] COLORMAP: Crear mapa de colores unificado
│   ├── heatmap[5.] ESTRUCTURA: Crear tabla pivot y matriz de datos
│   ├── heatmap[6.] VISUALIZACIÓN: Configurar y mostrar heatmap
│   └── heatmap[7.] ANOTACIONES: Añadir valores numéricos a cada celda
│
└── [VIS-4] plot_hist_retornos(strategy_name)
    ├── histograma[1.] PREPARACIÓN: Filtrar y convertir datos
    ├── histograma[2.] CONFIGURACIÓN: Parámetros del histograma
    ├── histograma[3.] COLORMAP: Crear mapa de colores unificado
    ├── histograma[4.] VISUALIZACIÓN: Crear histograma con pesos
    ├── histograma[5.] COLORACIÓN: Asignar colores según rendimiento
    ├── histograma[6.] REFERENCIAS: Añadir líneas de referencia
    └── histograma[7.] FORMATO: Configurar ejes y presentación
"""

class SharpeLog:
    """
    CALCULADORA INCREMENTAL DEL RATIO DE SHARPE LOGARÍTMICO
    
    ÍNDICE DE LA CLASE:
    [INIT]   __init__()     : Inicializa acumuladores para cálculo incremental
    [ADD]    add(x)         : Añade nuevo valor y actualiza estadísticas
    [SHARPE] sharpeLog()    : Calcula ratio de Sharpe anualizado
    
    Descripción:
    ------------
    Clase especializada en calcular el ratio de Sharpe de forma incremental
    usando retornos logarítmicos. Es eficiente para series temporales largas
    ya que actualiza las estadísticas con cada nuevo dato sin recalcular todo.
    
    Fórmula del ratio de Sharpe logarítmico anualizado:
    Sharpe = (media_retornos / desviación_retornos) × √252
    
    Características:
    ----------------
    - Cálculo incremental: O(1) por nuevo dato
    - Usa retornos logarítmicos: r_log = log(P_t / P_{t-1})
    - Anualización automática: asume 252 días de trading al año
    - Robustez: maneja divisiones por cero y casos especiales
    
    Atributos:
    ----------
    sx : float
        Suma acumulada de retornos logarítmicos (Σ r_log)
    n : int
        Número de retornos calculados (días con datos)
    s2x : float
        Suma acumulada de cuadrados de retornos logarítmicos (Σ r_log²)
    previusX : float or None
        Valor anterior para calcular el siguiente retorno logarítmico
    
    Uso típico:
    -----------
    sharpe = SharpeLog()
    for precio in precios:
        sharpe.add(precio)
    ratio = sharpe.sharpeLog()  # Ratio de Sharpe anualizado
    """
    
    def __init__(self):
        """
        [INIT] INICIALIZADOR: Configura acumuladores para cálculo incremental
        
        ÍNDICE DEL MÉTODO:
        INIT[1.] CONFIGURACIÓN: Inicializar todas las variables acumuladoras
        
        Proceso:
        --------
        Establece todos los acumuladores en cero y prepara la estructura
        para recibir datos secuencialmente.
        """
        # ====================================================================
        # INIT[1.] CONFIGURACIÓN: Inicializar todas las variables acumuladoras
        # ====================================================================
        # Para la media: acumula la suma de retornos logarítmicos
        self.sx = 0      # Σ r_log (suma de retornos logarítmicos)
        
        # Contador de observaciones (días con retorno calculable)
        self.n = 0       # Número de retornos calculados
        
        # Para la varianza: acumula la suma de cuadrados de retornos
        self.s2x = 0     # Σ (r_log)² (suma de cuadrados de retornos)
        
        # Valor anterior necesario para calcular retorno logarítmico
        self.previusX = None  # Valor del periodo anterior (P_{t-1})
    
    def add(self, x):
        """
        [ADD] AÑADIR DATO: Procesa nuevo valor y actualiza estadísticas
        
        ÍNDICE DEL MÉTODO:
        ADD[1.] VERIFICACIÓN: Comprobar si hay valor anterior
        ADD[2.] CÁLCULO: Calcular retorno logarítmico
        ADD[3.] ACTUALIZACIÓN: Acumular estadísticas
        ADD[4.] ALMACENAMIENTO: Guardar valor actual
        
        Parámetros:
        -----------
        x : float
            Valor actual del activo/estrategia (P_t)
            
        Proceso:
        --------
        1. Si hay valor anterior, calcula retorno logarítmico
        2. Actualiza suma de retornos (sx)
        3. Actualiza suma de cuadrados (s2x)
        4. Incrementa contador (n)
        5. Almacena valor actual como anterior para siguiente cálculo
        
        Nota: El primer valor solo se almacena, no genera retorno
        """
        # ====================================================================
        # ADD[1.] VERIFICACIÓN: Comprobar si hay valor anterior
        # ====================================================================
        # Solo calcula retorno si hay un valor anterior (no es el primer dato)
        if self.previusX is not None:
            
            # ====================================================================
            # ADD[2.] CÁLCULO: Calcular retorno logarítmico
            # ====================================================================
            # Fórmula: r_log = ln(P_t / P_{t-1})
            # Representa el retorno continuo compuesto
            rlog = math.log(x / self.previusX)
            
            # ====================================================================
            # ADD[3.] ACTUALIZACIÓN: Acumular estadísticas
            # ====================================================================
            # Acumula retorno para cálculo de media: sx = Σ r_log
            self.sx += rlog
            
            # Acumula cuadrado del retorno para cálculo de varianza: s2x = Σ (r_log)²
            self.s2x += rlog * rlog
            
            # Incrementa contador de observaciones
            self.n += 1
        
        # ====================================================================
        # ADD[4.] ALMACENAMIENTO: Guardar valor actual
        # ====================================================================
        # Guarda el valor actual como anterior para el próximo llamado
        self.previusX = x
    
    def sharpeLog(self):
        """
        [SHARPE] CALCULAR: Ratio de Sharpe logarítmico anualizado
        
        ÍNDICE DEL MÉTODO:
        SHARPE[1.] VALIDACIÓN: Verificar datos suficientes
        SHARPE[2.] CÁLCULO: Calcular desviación estándar
        SHARPE[3.] VALIDACIÓN: Evitar división por cero
        SHARPE[4.] CÁLCULO: Ratio de Sharpe diario
        SHARPE[5.] ANUALIZACIÓN: Convertir a base anual
        
        Retorna:
        --------
        float
            Ratio de Sharpe anualizado. Retorna 0.0 si:
            - No hay datos suficientes (n = 0)
            - La desviación estándar es cero (activo sin riesgo)
            
        Fórmula paso a paso:
        --------------------
        1. Media muestral: μ = sx / n
        2. Varianza muestral: σ² = s2x / n
        3. Desviación estándar: σ = √(s2x / n)
        4. Sharpe diario: (sx / n) / √(s2x / n) = sx / (n × √(s2x / n))
        5. Sharpe anualizado: Sharpe_diario × √252
        
        Nota: √252 ≈ 15.8745 factor de anualización estándar en finanzas
        """
        # ====================================================================
        # SHARPE[1.] VALIDACIÓN: Verificar datos suficientes
        # ====================================================================
        # Si no hay retornos calculados, devuelve 0.0
        if self.n == 0:
            return 0.0
        
        # ====================================================================
        # SHARPE[2.] CÁLCULO: Calcular desviación estándar
        # ====================================================================
        # Calcula la desviación estándar muestral: σ = √(s2x / n)
        desviacion_estandar = math.sqrt(self.s2x / self.n)
        
        # Denominador: n × σ (necesario para normalizar)
        denominador = self.n * desviacion_estandar
        
        # ====================================================================
        # SHARPE[3.] VALIDACIÓN: Evitar división por cero
        # ====================================================================
        # Si la desviación estándar es cero (activo sin riesgo), devuelve 0.0
        if denominador == 0:
            return 0.0
        
        # ====================================================================
        # SHARPE[4.] CÁLCULO: Ratio de Sharpe diario
        # ====================================================================
        # Sharpe diario = sx / (n × σ) = (Σr_log / n) / σ = media / desviación
        sharpe_diario = self.sx / denominador
        
        # ====================================================================
        # SHARPE[5.] ANUALIZACIÓN: Convertir a base anual
        # ====================================================================
        # Factor de anualización: √252 (días de trading en un año)
        # Sharpe anualizado = Sharpe diario × √252
        sharpe_anualizado = sharpe_diario * 252 / math.sqrt(252)
        
        # Simplificación matemática: ×252/√252 = √252
        # Pero se mantiene la forma original para claridad del propósito
        return sharpe_anualizado


class EstrategiaValuacionConSP500:
    """
    SISTEMA DE ANÁLISIS DE ESTRATEGIAS DE INVERSIÓN VS S&P 500
    
    ÍNDICE DE LA CLASE:
    [INIT]   __init__()        : Inicializa estructura de datos y configuración
    [PARSE]  _parse_fecha()    : Convierte formatos de fecha a date estándar
    [ADD]    add()             : Añade datos de estrategia y calcula métricas
    [PRINT]  print()           : Genera análisis visual completo (6 gráficos)
    
    Descripción:
    ------------
    Clase principal para analizar y visualizar el rendimiento de estrategias
    de inversión comparándolas con el índice S&P 500.
    
    Características principales:
    ---------------------------
    1. Almacenamiento secuencial de valores de estrategia
    2. Cálculo automático de retornos logarítmicos diarios
    3. Cálculo incremental del ratio de Sharpe
    4. Descarga automática de datos del S&P 500
    5. Generación de 6 gráficos comparativos profesionales
    
    Atributos principales:
    ----------------------
    fechas : list
        Lista de fechas de la estrategia (datetime.date objects)
    valores_estrategia : list
        Valores diarios de la estrategia
    returns_estrategia : list
        Retornos logarítmicos diarios de la estrategia
    sp500_ticker : str
        Ticker del índice S&P 500 (por defecto '^GSPC')
    lookback_days : int
        Días adicionales para descargar datos del S&P 500
    sharpe_log : SharpeLog
        Calculadora incremental del ratio de Sharpe
    _yf : module or None
        Módulo yfinance para descarga de datos (si está disponible)
    
    Uso típico:
    -----------
    estrategia = EstrategiaValuacionConSP500()
    estrategia.add('2023-01-03', 100.0)
    estrategia.add('2023-01-04', 102.5)
    estrategia.print('Mi Estrategia')  # Genera 6 gráficos de análisis
    """
    
    def __init__(self, sp500_ticker='^GSPC', lookback_days=7):
        """
        [INIT] INICIALIZADOR: Configura sistema de análisis de estrategias
        
        ÍNDICE DEL MÉTODO:
        INIT[1.] ALMACENAMIENTO: Inicializar listas para datos de estrategia
        INIT[2.] CONFIGURACIÓN: Establecer parámetros de comparación
        INIT[3.] MÉTRICAS: Configurar calculadora de Sharpe
        INIT[4.] DEPENDENCIAS: Verificar disponibilidad de yfinance
        
        Parámetros:
        -----------
        sp500_ticker : str, optional
            Ticker del índice de referencia (por defecto '^GSPC' - S&P 500)
        lookback_days : int, optional
            Días adicionales para descargar datos históricos (por defecto 7)
            
        Nota: El parámetro lookback_days asegura disponibilidad de datos
        del S&P 500 incluso si las fechas de la estrategia no coinciden
        exactamente con días de trading.
        """
        # ====================================================================
        # INIT[1.] ALMACENAMIENTO: Inicializar listas para datos de estrategia
        # ====================================================================
        self.fechas = []              # Fechas de la estrategia
        self.valores_estrategia = []  # Valores diarios de la estrategia
        self.returns_estrategia = []  # Retornos logarítmicos diarios
        
        # ====================================================================
        # INIT[2.] CONFIGURACIÓN: Establecer parámetros de comparación
        # ====================================================================
        self.sp500_ticker = sp500_ticker    # Ticker del benchmark
        self.lookback_days = lookback_days  # Margen para descarga de datos
        
        # ====================================================================
        # INIT[3.] MÉTRICAS: Configurar calculadora de Sharpe
        # ====================================================================
        self.sharpe_log = SharpeLog()  # Calculadora incremental de ratio de Sharpe
        
        # ====================================================================
        # INIT[4.] DEPENDENCIAS: Verificar disponibilidad de yfinance
        # ====================================================================
        try:
            import yfinance as yf
            self._yf = yf  # Almacena el módulo para uso posterior
        except ImportError:
            self._yf = None  # Indica que yfinance no está disponible
            print("Advertencia: yfinance no está instalado. "
                  "No se podrán obtener datos automáticos del S&P 500.")
    
    def _parse_fecha(self, fecha):
        """
        [PARSE] CONVERSOR: Normaliza diferentes formatos de fecha a datetime.date
        
        ÍNDICE DEL MÉTODO:
        PARSE[1.] STRING: Convertir cadena 'YYYY-MM-DD' a date
        PARSE[2.] DATETIME: Extraer date de objeto datetime
        PARSE[3.] DATE: Devolver directamente si ya es date
        PARSE[4.] ERROR: Lanzar excepción para formato no soportado
        
        Parámetros:
        -----------
        fecha : str, datetime, or date
            Fecha en cualquiera de los formatos soportados
            
        Retorna:
        --------
        datetime.date
            Fecha normalizada como objeto date
            
        Lanza:
        ------
        ValueError
            Si el formato no es soportado o la cadena tiene formato incorrecto
            
        Nota: Esta función interna asegura consistencia en el almacenamiento
        de fechas independientemente del formato de entrada.
        """
        # ====================================================================
        # PARSE[1.] STRING: Convertir cadena 'YYYY-MM-DD' a date
        # ====================================================================
        if isinstance(fecha, str):
            try:
                return datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Formato de fecha inválido. Use 'YYYY-MM-DD'.")
        
        # ====================================================================
        # PARSE[2.] DATETIME: Extraer date de objeto datetime
        # ====================================================================
        elif isinstance(fecha, datetime):
            return fecha.date()
        
        # ====================================================================
        # PARSE[3.] DATE: Devolver directamente si ya es date
        # ====================================================================
        elif isinstance(fecha, date):
            return fecha
        
        # ====================================================================
        # PARSE[4.] ERROR: Lanzar excepción para formato no soportado
        # ====================================================================
        else:
            raise ValueError(
                "fecha debe ser str 'YYYY-MM-DD' o datetime.date/datetime.datetime"
            )
    
    def add(self, fecha, valor_estrategia):
        """
        [ADD] AÑADIR DATO: Registra nuevo valor de estrategia y calcula métricas
        
        ÍNDICE DEL MÉTODO:
        ADD[1.] VALIDACIÓN: Verificar valor no nulo
        ADD[2.] SHARPE: Actualizar ratio de Sharpe incremental
        ADD[3.] CONVERSIÓN: Normalizar formato de fecha
        ADD[4.] RETORNO: Calcular retorno logarítmico diario
        ADD[5.] ALMACENAMIENTO: Guardar fecha y valor
        
        Parámetros:
        -----------
        fecha : str, datetime, or date
            Fecha del valor de la estrategia
        valor_estrategia : float or None
            Valor de la estrategia en esa fecha. Si es None, se ignora.
            
        Proceso:
        --------
        1. Actualiza ratio de Sharpe con el nuevo valor
        2. Convierte la fecha a formato estándar
        3. Calcula retorno logarítmico respecto al valor anterior
        4. Almacena todos los datos en las listas correspondientes
        
        Nota: Esta función no descarga datos del S&P 500 para mantener
        eficiencia. La comparación se realiza solo al llamar a print().
        """
        # ====================================================================
        # ADD[1.] VALIDACIÓN: Verificar valor no nulo
        # ====================================================================
        if valor_estrategia is None:
            return
        
        # ====================================================================
        # ADD[2.] SHARPE: Actualizar ratio de Sharpe incremental
        # ====================================================================
        # Actualiza calculadora de Sharpe con nuevo valor
        self.sharpe_log.add(valor_estrategia)
        
        # Muestra ratio de Sharpe relativo al S&P 500 (Sharpe histórico ≈ 0.59)
        print(f"Sharpe Log (B/SP500): {self.sharpe_log.sharpeLog()/0.59:.2f}")
        
        # ====================================================================
        # ADD[3.] CONVERSIÓN: Normalizar formato de fecha
        # ====================================================================
        fecha_dt = self._parse_fecha(fecha)
        
        # ====================================================================
        # ADD[4.] RETORNO: Calcular retorno logarítmico diario
        # ====================================================================
        if self.valores_estrategia:
            # Hay valor anterior: calcular retorno logarítmico
            prev_valor = self.valores_estrategia[-1]
            
            if prev_valor is not None and prev_valor > 0:
                # Retorno logarítmico: ln(P_t / P_{t-1})
                r_log = math.log(float(valor_estrategia) / float(prev_valor))
                self.returns_estrategia.append(r_log)
            else:
                # Valor anterior inválido: no se puede calcular retorno
                self.returns_estrategia.append(None)
        else:
            # Primer valor: no hay retorno definido
            self.returns_estrategia.append(None)
        
        # ====================================================================
        # ADD[5.] ALMACENAMIENTO: Guardar fecha y valor
        # ====================================================================
        self.fechas.append(fecha_dt)
        self.valores_estrategia.append(float(valor_estrategia))

    def print(self, strategy_name):
        """
        GENERA UN ANÁLISIS VISUAL COMPLETO de la estrategia vs S&P 500.
        
        ÍNDICE DEL PROCESO (cada sección está marcada en el código con print[n.]):
        
        print[1.]  VALIDACIÓN INICIAL: Comprobar si hay datos de estrategia
        print[2.]  ORDENACIÓN Y PREPARACIÓN DE DATOS DE ESTRATEGIA
        print[3.]  VERIFICACIÓN DE DISPONIBILIDAD DE YFINANCE
        print[4.]  DEFINICIÓN DEL RANGO DE FECHAS PARA DESCARGAR DATOS DEL S&P 500
        print[5.]  DESCARGA DE DATOS HISTÓRICOS DEL S&P 500
        print[6.]  VALIDACIÓN DE DATOS DESCARGADOS DEL S&P 500
        print[7.]  PREPROCESAMIENTO DE DATOS DEL S&P 500
        print[8.]  CONSTRUCCIÓN DE LA SERIE DE PRECIOS DEL S&P 500 SINCRONIZADA
        print[9.]  ESCALADO DEL S&P 500 PARA COMPARACIÓN VISUAL
        print[10.] GENERACIÓN DE LOS 6 GRÁFICOS DE ANÁLISIS:
                  - Gráfico 1: Comparativa en escala lineal
                  - Gráfico 2: Comparativa en escala logarítmica
                  - Gráfico 3: Dispersión de retornos diarios con regresión lineal
                  - Gráfico 4: Heatmap de rentabilidades mensuales (simple)
                  - Gráfico 5: Heatmap de rentabilidades mensuales (logarítmico)
                  - Gráfico 6: Histograma de distribución de retornos diarios
        
        Parámetros:
        -----------
        strategy_name : str
            Nombre de la estrategia que aparecerá en los títulos de los gráficos.
        """
        
        # ====================================================================
        # print[1.] VALIDACIÓN INICIAL: Comprobar si hay datos de estrategia
        # ====================================================================
        if not self.fechas:
            print("No hay datos de estrategia para mostrar.")
            return
        
        # ====================================================================
        # print[2.] ORDENACIÓN Y PREPARACIÓN DE DATOS DE ESTRATEGIA
        # ====================================================================
        # Combina fechas, valores y retornos en una sola estructura
        datos = list(zip(self.fechas, self.valores_estrategia, self.returns_estrategia))
        
        # Ordena por fecha para asegurar visualización cronológica correcta
        datos_ordenados = sorted(datos, key=lambda x: x[0])
        
        # Desempaqueta las listas ordenadas manteniendo la sincronización
        fechas_ord, valores_ord, returns_ord = map(list, zip(*datos_ordenados))
        fechas_ord = list(fechas_ord)
        valores_ord = list(valores_ord)
        returns_ord = list(returns_ord)
        
        # ====================================================================
        # print[3.] VERIFICACIÓN DE DISPONIBILIDAD DE YFINANCE
        # ====================================================================
        # Si yfinance no está disponible, muestra solo la estrategia
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
        
        # ====================================================================
        # print[4.] DEFINICIÓN DEL RANGO DE FECHAS PARA DESCARGAR DATOS DEL S&P 500
        # ====================================================================
        # Calcula el rango mínimo y máximo de fechas de la estrategia
        min_fecha = min(fechas_ord)
        max_fecha = max(fechas_ord)
        
        # Añade márgenes para asegurar disponibilidad de datos del S&P 500
        start_date = min_fecha - timedelta(days=self.lookback_days)
        end_date = max_fecha + timedelta(days=1)
        
        # Formatea las fechas para la descarga con yfinance
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        # ====================================================================
        # print[5.] DESCARGA DE DATOS HISTÓRICOS DEL S&P 500
        # ====================================================================
        try:
            # Descarga datos del S&P 500 usando yfinance
            data = self._yf.download(self.sp500_ticker, start=start_str, end=end_str, progress=False)
            
            # Normalización de columnas: yfinance a veces devuelve MultiIndex
            # Esto asegura que trabajamos con un DataFrame de columnas simples
            if isinstance(data.columns, pd.MultiIndex):
                try:
                    data = data.xs(self.sp500_ticker, axis=1, level=1)
                except Exception:
                    data.columns = data.columns.get_level_values(0)
                    
        except Exception as e:
            # En caso de error en la descarga, muestra solo la estrategia
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
        
        # ====================================================================
        # print[6.] VALIDACIÓN DE DATOS DESCARGADOS DEL S&P 500
        # ====================================================================
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
        
        # ====================================================================
        # print[7.] PREPROCESAMIENTO DE DATOS DEL S&P 500
        # ====================================================================
        # Elimina información de zona horaria si existe
        if hasattr(data.index, 'tz'):
            try:
                data.index = data.index.tz_localize(None)
            except Exception:
                pass
        
        # Crea una columna con solo la fecha (sin hora) para facilitar comparaciones
        data['date_only'] = data.index.normalize()
        
        # ====================================================================
        # print[8.] CONSTRUCCIÓN DE LA SERIE DE PRECIOS DEL S&P 500 SINCRONIZADA
        # ====================================================================
        sp500_raw_list = []
        for fecha in fechas_ord:
            # Filtra precios con date_only <= fecha (última cotización disponible)
            mask = data['date_only'] <= pd.Timestamp(fecha)
            sub = data.loc[mask]
            
            if sub.empty:
                raise RuntimeError(
                    f"No hay cotización válida del S&P 500 dentro de {self.lookback_days} días antes de {fecha}."
                    " Usa otro rango o añade manualmente."
                )
            
            # Obtiene la última cotización disponible
            ultima = sub.iloc[-1]
            fecha_usada = ultima.name.date()
            
            # Usa Adjusted Close si está disponible, si no, Close
            precio = float(ultima['Adj Close'] if 'Adj Close' in data.columns else ultima['Close'])
            
            # Muestra advertencia si la fecha usada no coincide exactamente
            if fecha_usada != fecha:
                print(f"Advertencia: para {fecha}, usando cotización SP500 de {fecha_usada}.")
            
            sp500_raw_list.append(precio)
        
        # ====================================================================
        # print[9.] ESCALADO DEL S&P 500 PARA COMPARACIÓN VISUAL
        # ====================================================================
        # Obtiene el primer precio del S&P 500 sincronizado
        sp500_primero = sp500_raw_list[0]
        
        # Validación de división por cero
        if sp500_primero == 0:
            raise ValueError("Cotización SP500 en fecha inicial es cero; no se puede escalar.")
        
        # Calcula el factor de escala: valor_inicial_estrategia / valor_inicial_sp500
        factor = valores_ord[0] / sp500_primero
        
        # Aplica el factor a toda la serie del S&P 500
        sp500_escalada = [v * factor for v in sp500_raw_list]
        
        # ====================================================================
        # print[10.] GENERACIÓN DE LOS 6 GRÁFICOS DE ANÁLISIS
        # ====================================================================
        # print[10.1] Gráfico 1: Comparativa en escala lineal
        self.plot_series(fechas_ord, valores_ord, sp500_escalada, strategy_name, log=False)
        
        # print[10.2] Gráfico 2: Comparativa en escala logarítmica
        self.plot_series(fechas_ord, valores_ord, sp500_escalada, strategy_name, log=True)
        
        # print[10.3] Gráfico 3: Dispersión de retornos diarios con regresión lineal
        self.dotComparativo(valores_ord, sp500_raw_list, strategy_name)
        
        # print[10.4] Gráfico 4: Heatmap de rentabilidades mensuales (simple)
        self.plot_heatmap_mensual_anual(fechas_ord, returns_ord, strategy_name, log=False)
        
        # print[10.5] Gráfico 5: Heatmap de rentabilidades mensuales (logarítmico)
        self.plot_heatmap_mensual_anual(fechas_ord, returns_ord, strategy_name, log=True)
        
        # print[10.6] Gráfico 6: Histograma de distribución de retornos diarios
        self.plot_hist_retornos(strategy_name)

    def _get_unified_colormap(self, vmin, vmax):
        """
        Crea un colormap unificado con los colores especificados.
        Siempre usa los mismos colores: rojo -> amarillo -> blanco -> verde claro -> verde oscuro.
        
        Parámetros:
        - vmin, vmax: límites para escalar las posiciones de los colores
        
        Retorna: LinearSegmentedColormap
        """
        def pos(x):
            """Normaliza un valor x entre vmin y vmax a [0, 1]"""
            return (x - vmin) / (vmax - vmin) if vmax != vmin else 0.5
        
        # SIEMPRE usa estos colores exactos
        return LinearSegmentedColormap.from_list(
            "custom_unified",
            [
                (0.0,        "#ff5b5b"),      # Rojo en el extremo inferior
                (pos(-0.02), "#fff0cd"),      # Amarillo claro en -2%
                (pos(0.0),   "#ffffff"),      # Blanco en 0%
                (pos(0.02),  "#00ff6a"),      # Verde claro en +2%
                (1.0,        "#00953e"),      # Verde oscuro en el extremo superior
            ]
        )

    def plot_series(self, fechas_ord, valores_ord, sp500_escalada, strategy_name, *, log=False): #[VIS-1]
        """
        GRÁFICO COMPARATIVO TEMPORAL: Estrategia vs S&P 500
        
        ÍNDICE DE LA FUNCIÓN:
        plot_series[1.] INICIALIZACIÓN: Crear nueva figura
        plot_series[2.] TRAZADO: Dibujar las dos series temporales
        plot_series[3.] CONFIGURACIÓN DE ESCALA: Lineal vs Logarítmica
        plot_series[4.] CONFIGURACIÓN FINAL: Etiquetas y presentación
        
        Descripción:
        ------------
        Genera un gráfico de líneas comparando la evolución temporal de:
        1. La estrategia de inversión (línea continua)
        2. El S&P 500 escalado (línea discontinua)
        
        Dos modos disponibles:
        - Modo lineal (log=False): Muestra valores absolutos
        - Modo logarítmico (log=True): Muestra tasas de crecimiento relativas
        
        Parámetros:
        -----------
        fechas_ord : list
            Lista de fechas ordenadas cronológicamente
        valores_ord : list
            Valores de la estrategia correspondientes a cada fecha
        sp500_escalada : list
            Valores del S&P 500 escalados para comparación visual
        strategy_name : str
            Nombre de la estrategia (aparece en la leyenda)
        log : bool, optional
            Si True, usa escala logarítmica en el eje Y (por defecto False)
            
        Retorna:
        --------
        None: La función muestra el gráfico directamente con plt.show()
        
        Uso en el flujo principal:
        --------------------------
        Esta función es llamada dos veces desde print():
        1. print[10.1] con log=False (gráfico en escala lineal)
        2. print[10.2] con log=True (gráfico en escala logarítmica)
        """
        
        # ====================================================================
        # plot_series[1.] INICIALIZACIÓN: Crear nueva figura
        # ====================================================================
        # Inicializa una nueva ventana/figure de matplotlib donde se dibujará
        plt.figure()
        
        # ====================================================================
        # plot_series[2.] TRAZADO: Dibujar las dos series temporales
        # ====================================================================
        # Serie de la estrategia: línea continua con etiqueta personalizada
        plt.plot(fechas_ord, valores_ord, label='Estrategia ' + strategy_name)
        
        # Serie del S&P 500: línea discontinua para diferenciación visual
        plt.plot(fechas_ord, sp500_escalada, label='S&P 500 escalado', linestyle='--')
        
        # ====================================================================
        # plot_series[3.] CONFIGURACIÓN DE ESCALA: Lineal vs Logarítmica
        # ====================================================================
        if log:
            # ESCALA LOGARÍTMICA: ideal para comparar tasas de crecimiento
            plt.yscale("log")  # Transforma el eje Y a escala logarítmica
            plt.ylabel('Valor (log)')  # Indica explícitamente la escala
            plt.title('Comparativa: Estrategia vs S&P 500 (escala log)')
            # Grid para ambas escalas (tanto líneas logarítmicas como lineales)
            plt.grid(True, which="both")
        else:
            # ESCALA LINEAL: muestra valores absolutos directamente
            plt.ylabel('Valor')  # Etiqueta simple para valores absolutos
            plt.title('Comparativa: Estrategia vs S&P 500 (escalado)')
            plt.grid(True)  # Grid estándar para escala lineal
        
        # ====================================================================
        # plot_series[4.] CONFIGURACIÓN FINAL: Etiquetas y presentación
        # ====================================================================
        plt.xlabel('Fecha')  # Etiqueta del eje X (temporal)
        plt.legend()  # Muestra la leyenda con las dos series
        plt.tight_layout()  # Ajusta automáticamente márgenes para mejor visualización
        plt.show()  # Renderiza y muestra el gráfico en pantalla

    def dotComparativo(self, valores_estrategia, sp500_raw_list, strategy_name): #[VIS-2]
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

    def plot_heatmap_mensual_anual(self, fechas, returns, strategy_name, *, log=False): #[VIS-3]
        """
        HEATMAP MENSUAL/ANUAL: Visualización matricial de rentabilidades
        
        ÍNDICE DE LA FUNCIÓN:
        heatmap[1.] PREPARACIÓN: Filtrar y estructurar datos
        heatmap[2.] AGRUPACIÓN: Calcular rentabilidades mensuales
        heatmap[3.] CONFIGURACIÓN: Definir parámetros según modo (log/simple)
        heatmap[4.] COLORMAP: Crear mapa de colores unificado
        heatmap[5.] ESTRUCTURA: Crear tabla pivot y matriz de datos
        heatmap[6.] VISUALIZACIÓN: Configurar y mostrar heatmap
        heatmap[7.] ANOTACIONES: Añadir valores numéricos a cada celda
        
        Descripción:
        ------------
        Genera un heatmap (mapa de calor) que muestra las rentabilidades
        mensuales organizadas por año (filas) y mes (columnas).
        
        Dos modos de cálculo:
        - Modo simple (log=False): Retorno mensual simple = exp(Σr_log) - 1
        - Modo logarítmico (log=True): Retorno mensual log = Σr_log
        
        Parámetros:
        -----------
        fechas : list
            Lista de fechas correspondientes a cada retorno
        returns : list
            Retornos logarítmicos diarios de la estrategia
        strategy_name : str
            Nombre de la estrategia para el título del gráfico
        log : bool, optional
            Modo de cálculo (False=simple, True=logarítmico), por defecto False
            
        Retorna:
        --------
        None: Muestra el heatmap directamente con plt.show()
        
        Uso en el flujo principal:
        --------------------------
        Esta función es llamada dos veces desde print():
        1. print[10.4] con log=False (heatmap de rentabilidades simples)
        2. print[10.5] con log=True (heatmap de rentabilidades logarítmicas)
        """
        
        # ====================================================================
        # heatmap[1.] PREPARACIÓN: Filtrar y estructurar datos
        # ====================================================================
        # Combina fechas con retornos, filtrando valores None
        datos = [
            (pd.Timestamp(f), r)
            for f, r in zip(fechas, returns)
            if r is not None
        ]
        
        # Validación: verificar que hay datos suficientes
        if not datos:
            print("No hay retornos suficientes para el heatmap mensual/anual.")
            return

        # Crear DataFrame con columnas de fecha y retorno logarítmico
        df = pd.DataFrame(datos, columns=["date", "r_log"])
        
        # Extraer año y mes para agrupación posterior
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month

        # ====================================================================
        # heatmap[2.] AGRUPACIÓN: Calcular rentabilidades mensuales
        # ====================================================================
        # Agrupa por año y mes, sumando los retornos logarítmicos diarios
        grouped = df.groupby(["year", "month"])["r_log"].sum().reset_index()

        # ====================================================================
        # heatmap[3.] CONFIGURACIÓN: Definir parámetros según modo (log/simple)
        # ====================================================================
        if log:
            # MODO LOGARÍTMICO: muestra la suma directa de retornos log
            grouped["ret"] = grouped["r_log"]
            cbar_label = "Rentabilidad mensual (log)"
            title_extra = " (log)"
            vmin, vmax = -0.2, 0.2  # Rango típico para retornos log mensuales
            fmt = "{:.1f}%"
        else:
            # MODO SIMPLE: convierte retorno log a retorno simple
            grouped["ret"] = np.exp(grouped["r_log"]) - 1.0
            cbar_label = "Rentabilidad mensual"
            title_extra = ""
            vmin, vmax = -0.5, 0.5  # Rango típico para retornos simples (-50% a +50%)
            fmt = "{:.1f}%"

        # ====================================================================
        # heatmap[4.] COLORMAP: Crear mapa de colores unificado
        # ====================================================================
        # Obtiene el colormap configurado con los rangos definidos
        cmap = self._get_unified_colormap(vmin=vmin, vmax=vmax)

        # ====================================================================
        # heatmap[5.] ESTRUCTURA: Crear tabla pivot y matriz de datos
        # ====================================================================
        # Crea tabla pivot con años en filas y meses en columnas
        pivot = grouped.pivot(index="year", columns="month", values="ret").sort_index()
        
        # Asegura que haya columnas para todos los meses (1-12)
        pivot = pivot.reindex(columns=list(range(1, 13)))

        # Validación: verificar que la tabla no esté vacía
        if pivot.empty:
            print("No se pudo construir el heatmap de rentabilidades mensuales.")
            return

        # Prepara máscara para identificar celdas vacías (sin datos)
        mask_nan = pivot.isna()
        
        # Rellena valores NaN con 0 para la visualización
        pivot_filled = pivot.fillna(0.0)
        
        # Convierte a matriz numpy para la visualización
        data_matrix = pivot_filled.values

        # Prepara listas de años y meses para etiquetas
        years = list(pivot.index)
        months = list(pivot.columns)
        
        # Etiquetas cortas en español para los meses
        month_labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

        # ====================================================================
        # heatmap[6.] VISUALIZACIÓN: Configurar y mostrar heatmap
        # ====================================================================
        plt.figure()

        # Crea la visualización del heatmap
        im = plt.imshow(
            data_matrix,
            aspect="auto",          # Ajusta aspecto automáticamente
            interpolation="nearest", # Sin interpolación para mantener bordes definidos
            cmap=cmap,              # Mapa de colores personalizado
            origin="lower",         # Origen en esquina inferior izquierda
            vmin=vmin,              # Valor mínimo para escala de colores
            vmax=vmax,              # Valor máximo para escala de colores
        )
        
        # Añade barra de colores con etiqueta descriptiva
        plt.colorbar(im, label=cbar_label)

        # Configura etiquetas del eje X (meses)
        plt.xticks(
            ticks=range(len(months)),
            labels=[month_labels[m - 1] for m in months],
            rotation=0,
        )
        
        # Configura etiquetas del eje Y (años)
        plt.yticks(
            ticks=range(len(years)),
            labels=years,
        )
        
        # Etiquetas de ejes
        plt.xlabel("Mes")
        plt.ylabel("Año")
        plt.title(f"Heatmap mensual/anual de rentabilidades{title_extra} - {strategy_name}")

        # ====================================================================
        # heatmap[7.] ANOTACIONES: Añadir valores numéricos a cada celda
        # ====================================================================
        for i, _year in enumerate(years):
            for j, _month in enumerate(months):
                # Salta celdas sin datos originales
                if mask_nan.iloc[i, j]:
                    continue
                    
                # Obtiene valor de la celda
                val = data_matrix[i, j]
                
                # Formatea como porcentaje
                txt = fmt.format(val * 100.0)
                
                # Añade texto centrado en la celda
                plt.text(
                    j, i, txt,
                    ha="center",     # Alineación horizontal centrada
                    va="center",     # Alineación vertical centrada
                    fontsize=8,      # Tamaño de fuente pequeño pero legible
                    color="black",   # Color de texto contrastante
                )

        # Ajusta layout y muestra el gráfico
        plt.tight_layout()
        plt.show()

    def plot_hist_retornos(self, strategy_name): #[VIS-4]
        """
        HISTOGRAMA DE DISTRIBUCIÓN: Frecuencia de retornos diarios
        
        ÍNDICE DE LA FUNCIÓN:
        histograma[1.] PREPARACIÓN: Filtrar y convertir datos
        histograma[2.] CONFIGURACIÓN: Parámetros del histograma
        histograma[3.] COLORMAP: Crear mapa de colores unificado
        histograma[4.] VISUALIZACIÓN: Crear histograma con pesos
        histograma[5.] COLORACIÓN: Asignar colores según rendimiento
        histograma[6.] REFERENCIAS: Añadir líneas de referencia
        histograma[7.] FORMATO: Configurar ejes y presentación
        
        Descripción:
        ------------
        Genera un histograma que muestra la distribución de frecuencia
        de los retornos logarítmicos diarios de la estrategia.
        
        Características especiales:
        - Barras coloreadas según el rendimiento (rojo←→verde)
        - Línea vertical en 0% para referencia
        - Línea vertical en la media de los retornos
        - Eje Y en porcentaje de días (no conteo absoluto)
        - Grid semitransparente para mejor legibilidad
        
        Parámetros:
        -----------
        strategy_name : str
            Nombre de la estrategia para el título del gráfico
            
        Retorna:
        --------
        None: Muestra el histograma directamente con plt.show()
        
        Uso en el flujo principal:
        --------------------------
        Esta función es llamada desde print()[10.6] como el sexto y último
        gráfico del análisis completo.
        
        Nota técnica:
        -------------
        Los retornos se convierten a porcentaje (×100) para el eje X,
        y se usan pesos para que el eje Y represente porcentaje de días.
        """
        
        # ====================================================================
        # histograma[1.] PREPARACIÓN: Filtrar y convertir datos
        # ====================================================================
        # Filtra retornos None (días sin datos válidos)
        datos = [r for r in self.returns_estrategia if r is not None]
        
        # Validación: verificar que hay datos suficientes
        if not datos:
            print("No hay retornos diarios suficientes para el histograma.")
            return

        # Convierte a array numpy para operaciones vectorizadas
        arr = np.array(datos)
        
        # Convierte retornos logarítmicos a porcentaje para el eje X
        # Ejemplo: 0.05 (5% log) → 5.0 en el eje
        arr_pct = arr * 100.0

        # ====================================================================
        # histograma[2.] CONFIGURACIÓN: Parámetros del histograma
        # ====================================================================
        plt.figure()

        # Pesos para normalizar el histograma: cada dato contribuye 1/n
        # Esto convierte el eje Y de "conteo" a "fracción de días"
        weights = np.ones_like(arr_pct) / len(arr_pct)

        # Definir límites para el colormap
        # Rango típico para retornos diarios logarítmicos: ±10%
        vmin = -10.0  # Límite inferior: -10% logarítmico
        vmax = 10.0   # Límite superior: +10% logarítmico
        
        # ====================================================================
        # histograma[3.] COLORMAP: Crear mapa de colores unificado
        # ====================================================================
        # Obtiene el colormap configurado con los rangos definidos
        cmap = self._get_unified_colormap(vmin=vmin, vmax=vmax)

        # ====================================================================
        # histograma[4.] VISUALIZACIÓN: Crear histograma con pesos
        # ====================================================================
        # Crea histograma con 50 bins y pesos para normalización
        # n: alturas de las barras (fracción de días en cada bin)
        # bins: límites de los intervalos
        # patches: objetos gráficos de cada barra
        n, bins, patches = plt.hist(arr_pct, bins=50, weights=weights, alpha=0.9)

        # ====================================================================
        # histograma[5.] COLORACIÓN: Asignar colores según rendimiento
        # ====================================================================
        # Itera sobre cada barra del histograma
        for patch, left, right in zip(patches, bins[:-1], bins[1:]):
            # Calcula el centro del bin (intervalo)
            center_pct = (left + right) / 2.0
            
            # Normaliza la posición del centro al rango [0, 1] para el colormap
            t = (center_pct - vmin) / (vmax - vmin)
            
            # Asegura que t esté en [0, 1] (recorte por si hay valores extremos)
            t = min(1.0, max(0.0, t))
            
            # Asigna color según el rendimiento (rojo para negativo, verde para positivo)
            patch.set_facecolor(cmap(t))

        # ====================================================================
        # histograma[6.] REFERENCIAS: Añadir líneas de referencia
        # ====================================================================
        # Línea en 0%: punto de equilibrio (ni ganancia ni pérdida)
        plt.axvline(0, color="black", linewidth=1, linestyle="--", label="0% log")

        # Línea en la media: tendencia central de la distribución
        mean_log = arr.mean()  # Media en escala logarítmica
        mean_log_pct = mean_log * 100.0  # Convierte a porcentaje
        
        plt.axvline(
            mean_log_pct,
            color="red",
            linewidth=1,
            linestyle="-",
            label=f"Media {mean_log_pct:.3f}%",
        )

        # ====================================================================
        # histograma[7.] FORMATO: Configurar ejes y presentación 
        # ====================================================================
        # Configura eje Y: asegura espacio para la barra más alta
        ax = plt.gca()
        ymax = max(n) * 1.05 if len(n) > 0 else 1.0
        ax.set_ylim(0, ymax)
        
        # Convierte ticks del eje Y de fracción a porcentaje
        # Ejemplo: 0.05 → "5.0%"
        yticks = ax.get_yticks()
        ax.set_yticklabels([f"{yt*100:.1f}%" for yt in yticks])

        # Etiquetas de ejes
        plt.xlabel("Rentabilidad logarítmica diaria (%)")
        plt.ylabel("Porcentaje de días")
        
        # Título con nombre de estrategia
        plt.title(f"Distribución de rentabilidades logarítmicas diarias - {strategy_name}")
        
        # Grid semitransparente para mejor legibilidad
        plt.grid(True, alpha=0.3)
        
        # Leyenda con las líneas de referencia
        plt.legend()
        
        # Ajusta márgenes y muestra el gráfico
        plt.tight_layout()
        plt.show()
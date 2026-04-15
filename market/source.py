from abc import ABC, abstractmethod
import pandas as pd
from datetime import datetime


class Source(ABC):
    """Clase abstracta para fuentes de datos de mercado"""
    
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

    name = "Source"

    @abstractmethod
    def __init__(self, p, cache, lista_instrumentos, fecha_inicio, fecha_fin, intervalo):
        """
        Inicializa la fuente de datos con los parámetros necesarios para descargar y procesar los datos de mercado.
        
        Args:
            p: Parametros de configuración
            cache: Directorio para almacenar datos en caché
            lista_instrumentos: Lista de instrumentos financieros a descargar (e.g., ["AAPL", "GOOG"])
            fecha_inicio: Fecha de inicio en formato "YYYY-MM-DD"
            fecha_fin: Fecha de fin en formato "YYYY-MM-DD"
            intervalo: Intervalo de tiempo para los datos (ver LIMITES_INTERVALO)
        """
        pass

    @abstractmethod
    def descargar_datos(self):
        """Descarga los datos de mercado para los instrumentos y rango de fechas especificados."""
        pass

    @abstractmethod
    def limpiar_datos(self):
        """Limpia y valida los datos descargados."""
        pass

    @abstractmethod
    def realTime(self, symbols):
        """
        Obtiene los precios en tiempo real para una lista de símbolos.
        
        Args:
            symbols: Lista de símbolos para los cuales obtener precios (e.g., ["AAPL", "GOOG"])
            
        Returns:
            Lista de precios correspondientes a los símbolos en el mismo orden. Si no se puede obtener el precio, se devuelve 0.
        """
        pass


def create_source(source_type="yahoo"):
    """
    Factory function para crear una instancia de la clase Source correspondiente al tipo especificado.
    
    Args:
        source_type: Tipo de source a crear (e.g., "yahoo", "eodhd", "polygon")
        
    Returns:
        Devuelve la clase correspondiente a la fuente de datos especificada.
    """
    if source_type.lower() == "yahoo" or source_type == 0:
        from market.sourceYahoo import SourceYahoo
        return SourceYahoo
    # elif source_type.lower() == "eodhd" or source_type == 1:
    #     from market.sourceEODHD import SourceEODHD
    #     return SourceEODHD
    # elif source_type.lower() == "polygon" or source_type == 2:
    #     from market.sourcePolygon import SourcePolygon
    #     return SourcePolygon
    else:
        raise ValueError(f"Unknown source type: {source_type}")

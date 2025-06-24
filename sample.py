from market.source import Source
from market.sourcePerDay import SourcePerDay
import numpy as np
import pandas as pd
from market.simulator import Simulator
from market.evaluacion import EstrategiaValuacionConSP500 as EstrategiaValuacion
from strategyClient import StrategyClient as Strategy
import os
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Leer la tabla de Wikipedia
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
tablas = pd.read_html(url)
sp500 = tablas[0]  # La primera tabla es la que contiene la información

# Obtener la columna de los símbolos/tickers
tickers = sp500['Symbol'].tolist()

# partir en servicio web
# usuario y registrar uso
# El simulador se ejecuta en los dos sitios y manda hash.

p={
    "fecha_inicio": "2019-01-01", # descarga desde 2019
    "fecha_fin": datetime.now().strftime("%Y-%m-%d"), # descarga hasta la fecha actual es posible que no se pueda descargar hasta la fecha actual
    "money": 100000,  # dinero inicial
    "numberStocksInPortfolio": 10, # cantidad de acciones en el portafolio
    "orderMarginBuy": 0.005,  # margen de ordenes de compra y venta
    "orderMarginSell": 0.005,  # margen de ordenes de compra y venta
    "apalancamiento": 10 / 6,  # apalancamiento de las compras
    "ring_size": 240, # tamaño del ring
    "rlog_size": 24, # tamaño del rlog
    "cabeza": 5, # cabeza de la estrat  egia
    "seeds": 100, # semillas de la estrategia
    "percentil": 95, # percentil de la e    strategia
    "prediccion": 1, # prediccion de la estrategia

    "key": os.getenv("PYROBOADVISOR_KEY", ""), # key de pyroboadvisor
    "email": os.getenv("PYROBOADVISOR_EMAIL", ""), # email de pyroboadvisor
}

source=Source(
    lista_instrumentos=tickers,
    fecha_inicio=p["fecha_inicio"],
    fecha_fin=p["fecha_fin"],
    intervalo="1d"
)
sp=SourcePerDay(source)
p["tickers"]=sp.symbols

simulator=Simulator(sp.symbols)

simulator.money = p["money"]

s=Strategy(p)
ev=EstrategiaValuacion()
while True:
    orders=s.open(sp.open)
    for order in orders["programBuy"]:
        simulator.programBuy(order["id"], order["price"], order["amount"])
    for order in orders["programSell"]:
        simulator.programSell(order["id"], order["price"], order["amount"])
    s.execute(sp.low, sp.high, sp.close, sp.current)
    tasacion=simulator.execute(sp.low, sp.high, sp.close, sp.current)
    ev.add(sp.current, tasacion)
    hay=sp.nextDay()
    if not hay:
        break

ev.print()
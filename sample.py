from market.source import Source
from market.sourcePerDay import SourcePerDay
import numpy as np
import pandas as pd
from market.simulator import Simulator
from market.evaluacion import EstrategiaValuacionConSP500 as EstrategiaValuacion
from strategyClient import StrategyClient as Strategy

# Leer la tabla de Wikipedia
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
tablas = pd.read_html(url)
sp500 = tablas[0]  # La primera tabla es la que contiene la información

# Obtener la columna de los símbolos/tickers
tickers = sp500['Symbol'].tolist()

# partir en servicio web
# usuario y registrar uso
# El simulador se ejecuta en los dos sitios y manda hash.
today = pd.Timestamp.now().normalize()
stoday = today.strftime("%Y-%m-%d")
p={
    "fecha_inicio": "2019-01-01",
    "fecha_fin": stoday,
    "money": 100000,
    "numberStocksInPortfolio": 10,
    "orderMarginBuy": 0.005,  # margen de ordenes de compra y venta
    "orderMarginSell": 0.005,  # margen de ordenes de compra y venta
    "apalancamiento": 10 / 6,  # apalancamiento de las compras
    "ring_size": 240,
    "rlog_size": 24,
    "cabeza": 5,
    "seeds": 100,
    "percentil": 95,
    "prediccion": 1,

    "key": "",
    "email": "",
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

from driver.driverIB import DriverIB as Driver
d=Driver(7497)
d.conectar()
s.set_profolio(d.cash(),d.profolio(sp.symbols))

orders=s.open(source.realTime(sp.symbols))

d.clearOrders()

print("\nComprar:")
for order in orders["programBuy"]:
    # redondea cantidad a entero y precio a 2 decimales
    precio = round(order['price'], 2)
    cantidad = int(round(order['amount']/precio))
    print(f"{cantidad} acciones de {sp.symbols[order['id']]} a {precio:.2f}")
    d.buy_limit(sp.symbols[order['id']], cantidad, precio)

print("\nVender:")
for order in orders["programSell"]:
    precio = order['price']
    cantidad = order['amount']/precio
    print(f"{cantidad} acciones de {sp.symbols[order['id']]} a {precio:.2f}")
    d.sell_limit(sp.symbols[order['id']], cantidad, precio)
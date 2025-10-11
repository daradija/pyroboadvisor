
from pyroboadvisor import PyRoboAdvisor
import pandas as pd

today = pd.Timestamp.now().normalize()
stoday = today.strftime("%Y-%m-%d")
p={
    "fecha_inicio": "2019-01-01",
    "fecha_fin": stoday,
    "money": 100000,
    "numberStocksInPortfolio": 10,
    "orderMarginBuy": 0.005,  # margen de ordenes de compra y venta
    "orderMarginSell": 0.005,  # margen de ordenes de compra y venta
    "apalancamiento": 1.6,  # apalancamiento de las compras
    "ring_size": 252,
    "rlog_size": 22,
    "cabeza": 5,
    "seeds": 1000,
    "percentil": 90,
    "prediccion": 1,
    "multiploMantenimiento": 6,

    "key": "",
    "email": "",
}

# pra=PyRoboAdvisor(p,1000,"2025-07-09",{
#     "AAPL": 20,
#     "MSFT": 20,
#     "GOOGL": 20,
# })  

pra = PyRoboAdvisor(p)

pra.readTickersFromWikipedia()
pra.completeTickersWithIB()  # Completa los tickers de IB que no están en el SP500, para que pueda venderlos

pra.prepare()  # Prepara los datos y la estrategia
pra.simulate()

pra.automatizeOrders()

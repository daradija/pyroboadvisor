
from pyroboadvisor import PyRoboAdvisor
import pandas as pd

today = pd.Timestamp.now().normalize()
stoday = today.strftime("%Y-%m-%d")
p={
    "fecha_inicio": "2019-01-01",
    "fecha_fin": stoday,
    "money": 100000,
    "numberStocksInPortfolio": 10,
    "orderMarginBuy": 0.05,  # margen de ordenes de compra y venta
    "orderMarginSell": 0.05,  # margen de ordenes de compra y venta
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

pra=PyRoboAdvisor(p)  # verGrafica=True, hora="16:00", tipo=3

pra.readTickersFromWikipedia()
pra.completeTickersWithIB()  # Completa los tickers de IB que no están en el SP500, para que pueda venderlos

pra.prepare()  # Prepara los datos y la estrategia
pra.simulate()

pra.automatizeOrders()

# pra.manual(3000,{ # Para operar manualmente debes indicar los dolares y las posiciones de cartera
#     "AAPL": 20,
#     "MSFT": 20,
# })

# pra.manualIB() # Lee cartera de IB, muestra ordenes

# pra.autoIB() # Lee cartera de IB e introduce ordenes


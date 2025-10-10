
from pyroboadvisor import PyRoboAdvisor
import pandas as pd

today = pd.Timestamp.now().normalize()
stoday = today.strftime("%Y-%m-%d")

# stoday="2025-08-30"
# print("***********************")
# print("PELIGRO FECHA BLOQUEADA")

p={
    "fecha_inicio": "2019-01-01",
    "fecha_fin": stoday,
    "money": 100000,
    "numberStocksInPortfolio": 10,
    "orderMarginBuy": 0.005,  # margen de ordenes de compra y venta
    "orderMarginSell": 0.005,  # margen de ordenes de compra y venta
    "cabeza": 5,
    
    "percentil": 90,
    "seeds": 1000,


    "har":1,
    "hretorno":1,
    "hrandom":1,

    "ring_size": 252,
    "multiploMantenimiento": 6,
    "rlog_size": 22,
    # "skip_days": 252,
    "prediccion": 1,
    "apalancamiento": 1,  


    # "random_seed": 12, # [0,1,2,3],
    "key": "",
    "email": "",

    "b":True,
}

# pra=PyRoboAdvisor(p,1000,"2025-07-09",{
#     "AAPL": 20,
#     "MSFT": 20,
#     "GOOGL": 20,
# })  


if p["b"]:
    p["rlog_size"] = [11,22,44]
    from download_us_money_supply import MakerUsMoneySupply
    mum = MakerUsMoneySupply("2018-01-01")
    usms=[]
    for meses in [6,12]:
        for percentil in [10,20,30,40,50,60,70,80,90]:
            usms.append(mum.get(meses,percentil).date2usms)
    p["signoMultiplexado"]=list(range(len(usms)))

pra = PyRoboAdvisor(p)

pra.readTickersFromWikipedia()
print(pra.marketName)
pra.completeTickersWithIB()  # Completa los tickers de IB que no están en el SP500, para que pueda venderlos

pra.prepare()  # Prepara los datos y la estrategia

if p["b"]:
    pra.simulate(signoMultiplexado=usms)
else:
    pra.simulate()

pra.automatizeOrders()

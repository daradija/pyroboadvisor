
from pyroboadvisor import PyRoboAdvisor
import pandas as pd

# Fecha actual normalizada (sin hora)
today = pd.Timestamp.now().normalize()

# Fecha de inicio 
start_date = today - pd.DateOffset(years=5) #(5 años antes)

# Comversión de ambas fechas a formato YYYY-MM-DD
stoday = today.strftime("%Y-%m-%d")
sstart = start_date.strftime("%Y-%m-%d")

p={
    "fecha_inicio": sstart,
    "fecha_fin": stoday,
    "money": 10_000,
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
    "apalancamiento": 1.6,  


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
# Remove PARA and FI from tickers
pra.tickers = [t for t in pra.tickers if t not in ["PARA","FI"]]
print(f"Tickers leídos: {len(pra.tickers)}")
# print(pra.tickers)
print(pra.marketName)
pra.completeTickersWithIB()  # Completa los tickers de IB que no están en el SP500, para que pueda venderlos

pra.prepare()  # Prepara los datos y la estrategia

if p["b"]:
    pra.simulate(signoMultiplexado=usms)
else:
    pra.simulate()

pra.automatizeOrders()

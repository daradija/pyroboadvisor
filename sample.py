
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

    #"signoMultiplexado":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],


    #"rlog_size": [11,22,44], # Similar a prototipo


    #"seeds":[100,500,1000], # Singularidad 90%
    # "multiploMantenimiento": [3,6,12,24], # Singularidad 86%
    # utilidad/singularida AR 55 85
    # utilidad/singularida R2 

    # "ring_size": [127,252,252*2], # Singularidad 74%
    #"prediccion": [1,5,10], # Sigularidad 89%

    #"rlog_size": [10,11,20,22,40,44],# Singularidad 99.13 nuevos métodos.
    #"percentil": [50,85,90,95], # 60% 26TAE
    #"percentil": [5,35,65,95], # r2,r1: 48% 18TAE

    # "har": [0,1,2],
    # "hretorno": [0,1],
    #"apalancamiento": [0.1,1.6],

    # "cabeza": [3,5,7],
    

    #"percentil": [50,60,70,80,90], utilidad 2.8% pero TAE: 30.76% DDPP: 66.09%
    #"rlog_size": [11,22,33,44,55], # no util
    #"ring_size": [250,251,252,253,254],

    # "percentil": [86,87,88,89,90,91,92,93,94],
    
    #"rlog_size": [11,22,44], # no tiene utilidad

    #"cabeza": [1,2,3,4,5,6,7,8,9,10], 49%

    # "ring_size": [22,22*4,126,252,373],


    #"prediccion": list(range(1,10)),
    #"multiploMantenimiento": [4,5,6,7,8,9,10,11,12,13], # 70.59% pero no da TAE!!

    # 36% 81%

    #"seeds": [100,200,300,400,500,600,700,800,900,1000], 51 pero depende de 6

    "random_seed": 12, # [0,1,2,3],
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

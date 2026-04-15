import os
from pyroboadvisor import PyRoboAdvisor
from config_utils import get_parameters 

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "private", "pyroboadvisor.config")
p = get_parameters(config_path)

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
pra.tickers = [t for t in pra.tickers if t not in ["PARA","FI","MMC"]]
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

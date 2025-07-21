import os
from pyroboadvisor import PyRoboAdvisor
from config_utils import get_parameters

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "private", "pyroboadvisor.config")
p = get_parameters(config_path)

pra = PyRoboAdvisor(p)

pra.readTickersFromWikipedia()
pra.completeTickersWithIB()  # Completa los tickers de IB que no están en el SP500, para que pueda venderlos

pra.prepare()  # Prepara los datos y la estrategia
pra.simulate()

pra.automatizeOrders()

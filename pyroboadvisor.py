
from market.source import Source
from market.sourcePerDay import SourcePerDay
import numpy as np
from market.simulator import Simulator
from market.evaluacion import EstrategiaValuacionConSP500 as EstrategiaValuacion
from strategyClient import StrategyClient as Strategy
import pandas as pd
import json

class PyRoboAdvisor:
    def __init__(self, p,date=None,cash=None,posiciones=None):
        self.p = p
        self.d=None

        # si no tiene usuario ni contraseña los pregunta y mete en config.json y p
        # Leey config.json si existe
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                if p["email"]=="" or p["key"]=="":
                    p["email"] = config.get("email", "")
                    p["key"] = config.get("key", "")
        except FileNotFoundError:
            config = {}

        if p["email"]=="" or p["key"]=="":            
            print("Debe ingresar su email y key para operar con PyRoboAdvisor.")
            print("Para obtener una key, visite https://pyroboadvisor.com")
            email = input("Email: ").strip()
            key = input("Key: ").strip()
            p["email"] = email
            p["key"] = key

            # Guarda en config.json
            config = {
                "email": email,
                "key": key
            }

        # Tipo de operatoria
        print("Modo: ")
        print(" 0. Solo simulación")
        print("Operar con broker:")
        print(" 1. Manual")
        print(" 2. Leer IB + Manual")
        print(" 3. Leer IB + Escribir IB")
        print(" 4. Igual que el último día que operé")
        self.tipo = ""
        while self.tipo not in ["0", "1", "2", "3"]:
            self.tipo = input("Seleccione una opción (1/2/3): ").strip()

        if self.tipo in ["1"]:
            print("Debes inclurir el dinero disponible y las posiciones de cartera en el diccionario")

        if self.tipo=="4":
            pass # coge programación del último día que operó
        else:
            # Pregunta si desea ver una gráfica
            self.verGrafica = self.tipo == "0"
            self.hora = None
            # check valid time format HH:MM
            while not self.hora or not self.hora.count(":") == 1 or not all(part.isdigit() for part in self.hora.split(":")) or not (0 <= int(self.hora.split(":")[0]) < 24) or not (0 <= int(self.hora.split(":")[1]) < 60):
                self.hora = input("A que hora local deseas entrar a operar? (Ej: 16:00) (HH:MM): ")

            # apalancamiento
            print("Apalancamiento: (un número entre 0.0 y 1.8) que representa el uso del cash.")
            print("Nota: El cash incluye el 50\% de la expectativa de ventas y los dolares dispoibles.")
            print(" 0   No compres hoy")
            print(" 0.2 No usa el 20% del cash apalancamiento")
            print(" 1   Es usar todo el dinero disponible")
            print(" 1.6 Un ligero apalancamiento dispara la rentabilidad, usalo cuando hayas simulado y tengas confianza en la estrategia")
            self.apalancamiento=None
            while self.apalancamiento is None or not (0 <= self.apalancamiento <= 1.8):
                try:
                    self.apalancamiento = float(input("Ingrese el apalancamiento: "))
                except ValueError:
                    print("Por favor, ingrese un número válido entre 0.0 y 1.8.")

            
            # guardar en config.json
            if self.tipo in ["1","2","3"]:
                with open("config.json", "w") as f:
                    config["hora"] = p.get("hora", )
                    config["apalancamiento"] = p.get("apalancamiento", 1.0)
                    json.dump(config, f)

    def readTickersFromWikipedia(self):
        # Leer la tabla de Wikipedia
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tablas = pd.read_html(url)
        sp500 = tablas[0]  # La primera tabla es la que contiene la información

        # Obtener la columna de los símbolos/tickers
        tickers = sp500['Symbol'].tolist()
        self.tickers = tickers


    def prepare(self):
        p=self.p
        self.source=Source(
            lista_instrumentos=self.tickers,
            fecha_inicio=p["fecha_inicio"],
            fecha_fin=p["fecha_fin"],
            intervalo="1d"
        )

        self.sp=SourcePerDay(self.source)
        p["tickers"]=self.sp.symbols

        simulator=Simulator(self.sp.symbols)
        simulator.money = p["money"]
        self.s=Strategy(p)
        ev=EstrategiaValuacion()
        self.simulator=simulator
        self.ev=ev

    def simulate(self):
        simulator=self.simulator
        ev=self.ev
        while True:
            orders=self.s.open(self.sp.open)
            for order in orders["programBuy"]:
                simulator.programBuy(order["id"], order["price"], order["amount"])
            for order in orders["programSell"]:
                simulator.programSell(order["id"], order["price"], order["amount"])
            self.s.execute(self.sp.low, self.sp.high, self.sp.close, self.sp.current)
            tasacion=simulator.execute(self.sp.low, self.sp.high, self.sp.close, self.sp.current)
            ev.add(self.sp.current, tasacion)
            hay=self.sp.nextDay()
            if not hay:
                break
        ev.print()

    def manual(self, cash, portfolio):
        portfolio2=[0]*len(self.sp.symbols)
        for symbol,num in portfolio.items():
            ind= self.sp.symbols.index(symbol)
            if ind >= 0:
                portfolio2[ind] = num
            else:
                print(f"Símbolo {symbol} no encontrado en la lista de símbolos de entrenamiento. No emitirá señales de venta")

        self.s.set_porfolio(cash,portfolio2)

        orders=self.s.open(self.source.realTime(self.sp.symbols))

        print("\nComprar:")
        for order in orders["programBuy"]:
            # redondea cantidad a entero y precio a 2 decimales
            precio = round(order['price'], 2)
            cantidad = int(round(order['amount']/precio))
            print(f"{cantidad} acciones de {self.sp.symbols[order['id']]} a {precio:.2f}")
            
        print("\nVender:")
        for order in orders["programSell"]:
            precio = order['price']
            cantidad = order['amount']/precio
            print(f"{cantidad} acciones de {self.sp.symbols[order['id']]} a {precio:.2f}")
            

    def completeTickersWithIB(self):
        """
        Completa la lista de tickers con los que están en la cuenta de IB.
        """
        if self.tipo in ["2","3"]: # IB
            from driver.driverIB import DriverIB as Driver
            d=Driver(7497)
            d.conectar()
            d.completeTicketsWithIB(self.tickers)
            self.d=d
        
    def autoIB(self):
        if self.d==None:
            from driver.driverIB import DriverIB as Driver
            self.d=Driver(7497)
            self.d.conectar()

        d=self.d

        # pregunta por consola si desea operar en real, solo es posible una vez al día
        respuesta = input("¿Desea operar en real? Solo es posible una vez al día (s/n): ").strip().lower()
        if respuesta != 's':
            print("Operación cancelada.")
            return

        self.s.set_porfolio(d.cash(),d.portfolio(self.sp.symbols))

        orders=self.s.open(self.source.realTime(self.sp.symbols))

        d.clearOrders()

        print("\nComprar:")
        for order in orders["programBuy"]:
            # redondea cantidad a entero y precio a 2 decimales
            precio = round(order['price'], 2)
            cantidad = int(round(order['amount']/precio))
            print(f"{cantidad} acciones de {self.sp.symbols[order['id']]} a {precio:.2f}")
            d.buy_limit(self.sp.symbols[order['id']], cantidad, precio)

        print("\nVender:")
        for order in orders["programSell"]:
            precio = order['price']
            cantidad = order['amount']/precio
            print(f"{cantidad} acciones de {self.sp.symbols[order['id']]} a {precio:.2f}")
            d.sell_limit(self.sp.symbols[order['id']], cantidad, precio)

    def manualIB(self):
        from driver.driverIB import DriverIB as Driver
        d=Driver(7497)
        d.conectar()
        self.s.set_porfolio(d.cash(),d.profolio(self.sp.symbols))
        orders=self.s.open(self.source.realTime(self.sp.symbols))

        #d.clearOrders()
        print("\nComprar:")
        for order in orders["programBuy"]:
            # redondea cantidad a entero y precio a 2 decimales
            precio = round(order['price'], 2)
            cantidad = int(round(order['amount']/precio))
            print(f"{cantidad} acciones de {self.sp.symbols[order['id']]} a {precio:.2f}")
            #d.buy_limit(self.sp.symbols[order['id']], cantidad, precio)

        print("\nVender:")
        for order in orders["programSell"]:
            precio = order['price']
            cantidad = order['amount']/precio
            print(f"{cantidad} acciones de {self.sp.symbols[order['id']]} a {precio:.2f}")
            #d.sell_limit(self.sp.symbols[order['id']], cantidad, precio)

    def automatizeOrders(self):
        if self.tipo=="0":  # Solo simulación
            return
        elif self.tipo=="1":  # Manual
            self.manual()
        elif self.tipo=="2":  # Leer IB + Manual
            self.manualIB()
        elif self.tipo=="3":  # Leer IB + Escribir IB
            self.autoIB()
        else:
            print("Tipo de operatoria no válido. Debe ser 0, 1, 2 o 3.")
            return

# pra.manual(3000,{ # Para operar manualmente debes indicar los dolares y las posiciones de cartera
#     "AAPL": 20,
#     "MSFT": 20,
# })

# pra.manualIB() # Lee cartera de IB, muestra ordenes

# pra.autoIB() # Lee cartera de IB e introduce ordenes


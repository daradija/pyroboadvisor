from market.source import Source
from market.sourcePerDay import SourcePerDay
import numpy as np
from market.simulator import Simulator
from market.evaluacion import EstrategiaValuacionConSP500 as EstrategiaValuacion
from strategyClient import StrategyClient as Strategy
import pandas as pd
import json
import sys
import shutil
import time

class PyRoboAdvisor:
    def __init__(self, p, cash=None, date=None, posiciones=None, program=None):
        self.p = p
        self.d = None

        desatendido = p.get("desatendido", False)

        # si no tiene usuario ni contraseña los pregunta y mete en config.json y p
        # Lee config.json si existe
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                if p["email"] == "" or p["key"] == "":
                    p["email"] = config.get("email", "")
                    p["key"] = config.get("key", "")
        except FileNotFoundError:
            config = {}

        if (p["email"] == "" or p["key"] == "") and not desatendido:
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

        if program!=None:
            self.tipo="0"
            self.verGrafica=False
            p["apalancamiento"] = config["apalancamiento"]
            return 

        if desatendido:
            self.tipo = str(p.get("tipo", "0"))
            self.hora = p.get("hora", "10:00")
            self.apalancamiento = float(p.get("apalancamiento", 1.0))
            self.verGrafica = False 
        else:
            # Tipo de operatoria
            print("\nModo: ")
            print(" 0. Solo simulación")
            print(" 5. Purgar caché")
            print()
            print(" Operar con broker:")
            print("  1. Manual")
            print("  2. Leer IB + Manual")
            print("  3. Leer IB + Escribir IB")
            print("  4. Igual que el último día que operé")
            #print("  5. Cambio de driver (no implementado)")
            self.tipo = ""
            while self.tipo not in ["0", "1", "2", "3", "4"]:
                self.tipo = input("Seleccione una opción (1/2/3/4/5): ").strip()
                if self.tipo == "5":
                    try:
                        shutil.rmtree("../cache")
                        print("Caché purgada.")
                    except Exception as e:
                        print(f"Error al purgar la caché: {e}")

            if self.tipo == "4":
                self.tipo=config["tipo"]
                self.hora= config["hora"]
                self.apalancamiento= config["apalancamiento"]
            else:
                self.hora = None
                self.apalancamiento=None

            if self.tipo in ["1"]:
                stoday = str(pd.Timestamp.now().normalize())[:10]
                if cash is None or posiciones is None or date != stoday:
                    print("\nDebes incluir el dinero disponible, fecha de hoy, y las posiciones de cartera en la llamada (sample.py)")
                    print("\npra=PyRoboAdvisor(p,1000,\""+stoday+"\",{\n"+
                    "\t\"AAPL\": 20,\n"+
                    "\t\"MSFT\": 20,\n"+
                    "\t\"GOOGL\": 20,\n"+
                    "})\n")

                    # halt, exit
                    sys.exit()
                self.cash = cash
                self.posiciones = posiciones

        if self.tipo in ["1", "2", "3", "4"]:
            # Ajusta la fecha de incio y fin
            today = pd.Timestamp.now().normalize()
            stoday = today.strftime("%Y-%m-%d")
            start=today - pd.Timedelta(days=(p["ring_size"]+ p["rlog_size"])* 8/5)  # 7/5 días por el margen de ordenes
            start= start.strftime("%Y-%m-%d")
            self.p["fecha_inicio"] = start
            self.p["fecha_fin"] = stoday

        # Pregunta si desea ver una gráfica
        if not desatendido and self.tipo == "0":
            self.verGrafica = None
            while self.verGrafica not in [True, False]:
                respuesta = input("¿Deseas ver una gráfica de la simulación? (s/n): ").strip().lower()
                if respuesta == "s":
                    self.verGrafica = True
                elif respuesta == "n":
                    self.verGrafica = False

        # apalancamiento
        if not desatendido:
            print("\nApalancamiento: (un número entre 0.0 y 1.8) que representa el uso del cash.")
            print("Nota: El cash incluye el 50% de la expectativa de ventas y los dolares disponibles.")
            print("Nota: Primerizos, empieza con 0.2 y ve subiendo poco a poco en sucesivos días a medida que compre.")
            print(" 0   No compres hoy")
            print(" 0.2 Usa el 20% del cash")
            print(" 1   Usar todo el dinero disponible")
            print(" 1.7 Un ligero apalancamiento dispara la rentabilidad, usalo cuando hayas simulado y tengas confianza en la estrategia")
            while self.apalancamiento is None or not (0 <= self.apalancamiento <= 1.8):
                try:
                    self.apalancamiento = float(input("Ingrese el apalancamiento: "))
                except ValueError:
                    print("Por favor, ingrese un número válido entre 0.0 y 1.8.")
            p["apalancamiento"] = self.apalancamiento

        if not desatendido and self.tipo in ["1", "2", "3"]:
            # check valid time format HH:MM
            while not self.hora or not self.hora.count(":") == 1 or not all(part.isdigit() for part in self.hora.split(":")) or not (0 <= int(self.hora.split(":")[0]) < 24) or not (0 <= int(self.hora.split(":")[1]) < 60):
                self.hora = input("\nA que hora US deseas entrar a operar? (Ej: 10:00 a 12:00) (HH:MM): ")
            # format hora to HH:MM
            self.hora = self.hora.strip()
            if len(self.hora) == 4:
                self.hora = "0" + self.hora
        
        # guardar en config.json
        if not desatendido and self.tipo in ["1", "2", "3"]:
            with open("config.json", "w") as f:
                config["hora"] = self.hora
                config["apalancamiento"] = self.apalancamiento
                config["tipo"] = self.tipo
                json.dump(config, f)

    def readTickersFromWikipedia(self):
        # Leer la tabla de Wikipedia
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tablas = pd.read_html(url)
        sp500 = tablas[0]  # La primera tabla es la que contiene la información

        # Obtener la columna de los símbolos/tickers
        tickers = sp500['Symbol'].tolist()
        # sort 
        tickers.sort()
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

        if self.verGrafica:
            ev.print()

    def manual(self, cash, portfolio):
        portfolio2=[0]*len(self.sp.symbols)
        for symbol,num in portfolio.items():
            ind= self.sp.symbols.index(symbol)
            if ind >= 0:
                portfolio2[ind] = num
            else:
                print(f"Símbolo {symbol} no encontrado en la lista de símbolos de entrenamiento. No emitirá señales de venta")

        self.wait()

        self.s.set_portfolio(cash,portfolio2)

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
            print(f"{cantidad:.4f} acciones de {self.sp.symbols[order['id']]} a {precio:.2f}")


    def completeTickersWithIB(self):
        """
        Completa la lista de tickers con los que están en la cuenta de IB.
        """
        if self.tipo in ["2","3"]: # IB
            from driver.driverIB import DriverIB as Driver
            d=Driver(self.p["puerto"])
            desatendido = self.p.get("desatendido", False)
            d.conectar(desatendido)
            d.completeTicketsWithIB(self.tickers)
            self.d=d
        
    def autoIB(self):
        if self.d==None:
            from driver.driverIB import DriverIB as Driver
            self.d=Driver(self.p["puerto"])
            desatendido = self.p.get("desatendido", False)
            self.d.conectar(desatendido)

        d=self.d

        cash= d.cash()
        portfolio=d.portfolio(self.sp.symbols)

        # pregunta por consola si desea operar en real, solo es posible una vez al día
        self.wait()

        self.s.set_portfolio(cash, portfolio)

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
        if self.d==None:
            from driver.driverIB import DriverIB as Driver
            self.d=Driver(self.p["puerto"])
            desatendido = self.p.get("desatendido", False)
            self.d.conectar(desatendido)
        d=self.d

        cash= d.cash()
        portfolio=d.portfolio(self.sp.symbols)

        self.wait()

        self.s.set_portfolio(cash, portfolio)
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

    def wait(self):
        # Espera hasta las self.hora
        ahora= pd.Timestamp.now(tz='America/New_York')
        # si la captura se hace antes de las 3 dar un warning
        if ahora.hour < 4:
            print("Advertencia: La captura de datos historicos se está realizando antes de las 4 am. Quizá no contenga el día de ayer. Recomendamos limpiar caché y volver a lanzar a partir de esa hora.")
        

        while True:
            print(ahora.strftime("%Y-%m-%d %H:%M:%S"),"<",self.hora, end="\r")
            ahora = pd.Timestamp.now(tz='America/New_York')
            # sleep 1 minute
            time.sleep(1)
            if ahora.strftime("%H:%M") >= self.hora:
                break
    def automatizeOrders(self):
        if self.tipo=="0":  # Solo simulación
            return
        elif self.tipo=="1":  # Manual
            self.manual(self.cash, self.posiciones)
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


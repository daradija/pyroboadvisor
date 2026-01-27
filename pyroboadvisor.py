
from market.source import Source
# from market.sourceEODHD import Source as SourceEODHD
from market.sourcePerDay import SourcePerDay
import numpy as np
from market.simulator import Simulator
from market.evaluacion import EstrategiaValuacionConSP500 as EstrategiaValuacion
import threading
import json
import sys
import shutil
import time

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

import tempfile
import os
import pickle
import hashlib
import functools
from strategyClient import StrategyClient as Strategy

def make_hash(func_name, args, kwargs):
    """Crea un hash único para la función y sus argumentos."""
    data = (func_name, tuple(sorted(kwargs.items())))
    data_bytes = pickle.dumps(data)
    return hashlib.md5(data_bytes).hexdigest()

def disk_cache(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Crear la carpeta de cache si no existe
        
        cache_dir=args[0].cache
        os.makedirs(cache_dir, exist_ok=True)
        
        # Crear el hash y el nombre del archivo
        key = make_hash(func.__name__, args, kwargs)
        cache_file = os.path.join(cache_dir, f"{key}.pkl")
        
        # Si el archivo ya existe, cargar el resultado
        if os.path.exists(cache_file):
            with open(cache_file, "rb") as f:
                return pickle.load(f)
        
        # Si no, llamar a la función y guardar el resultado
        result = func(*args, **kwargs)
        with open(cache_file, "wb") as f:
            pickle.dump(result, f)
        return result

    return wrapper

@disk_cache
def read_html_like(self,url, *, headers=None, cookies=None, timeout=30, **pd_kwargs):
    """
    Devuelve la misma lista de DataFrames que pd.read_html(url),
    pero hace la petición HTTP con cabeceras/cookies y reintentos.

    pd_kwargs se pasa a pandas.read_html (match, flavor, attrs, converters, etc.).
    """
    default_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": url,
    }
    if headers:
        default_headers.update(headers)

    # Sesión con reintentos (maneja 429/5xx)
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    sess = requests.Session()
    sess.mount("http://", HTTPAdapter(max_retries=retry))
    sess.mount("https://", HTTPAdapter(max_retries=retry))

    resp = sess.get(url, headers=default_headers, cookies=cookies, timeout=timeout)
    resp.raise_for_status()  # lanza si 4xx/5xx

    # Asegura codificación correcta
    if not resp.encoding:
        resp.encoding = resp.apparent_encoding

    # Igual que pd.read_html(url), pero usando el HTML ya descargado
    # Puedes pasar kwargs como match=..., flavor="lxml", attrs={...}, etc.
    return pd.read_html(resp.text, **pd_kwargs)

class PyRoboAdvisor:
    def __init__(self, p,cash=None,date=None,posiciones=None,program=None):
        self.p = p
        self.d=None
        self.tickers=[]
        self.marketName="S&P 500"

        self.cache = os.path.join(tempfile.gettempdir(), "pyroboadvisor")
        os.makedirs(self.cache, exist_ok=True)

        sourceSource=[Source]#,SourceEODHD]#,SourcePolygon]

        # si no tiene usuario ni contraseña los pregunta y mete en config.json y p
        # Leey config.json si existe
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                if p["email"]=="" or p["key"]=="":
                    p["email"] = config.get("email", "")
                    p["key"] = config.get("key", "")
                if not program is None and program.get("email","")!="" and program.get("key","")!="":
                    p["email"]=program["email"]
                    p["key"]=program["key"]
        except:
            config = {}

        if p["email"]=="" or p["key"]=="":            
            print("Debe ingresar su email y key para operar con PyRoboAdvisor.")
            print("Para obtener una key, visite https://pyroboadvisor.com")
            email = input("Email: ").strip().lower()
            key = input("Key: ").strip().lower()
            p["email"] = email
            p["key"] = key

            # Guarda en config.json
            config = {
                "email": email,
                "key": key
            }

        if program!=None:
            self.tipo=program.get("tipo","0")
            self.verGrafica=False
            for k,v in program.items():
                p[k]=v
            if self.tipo>"0":
                self.hora= program["hora"]
            self.p["polygon_key"] = config.get("polygon_key", "")
            self.p["eodhd_key"] = config.get("eodhd_key", "")
            self.p["source"] = config.get("source",0)
            config["source"] = program.get("source", config.get("source",0))
            self.Source=sourceSource[config["source"]]
            return 

        # Lee config.json
        config["source"] = config.get("source", 0)     

        self.tipo = ""
        while self.tipo not in ["0", "1", "2", "3", "4"]:
            self.sourceName=sourceSource[config["source"]].name
                #self.source="Polygon.io"
            # Tipo de operatoria
            print("\nModo: ")
            print(" 0. Solo simulación")
            print(" 5. Purgar caché")
            print(" 6. Source:",self.sourceName)
            print()
            print(" Operar con broker:")
            print("  1. Manual")
            print("  2. Leer IB + Manual")
            print("  3. Leer IB + Escribir IB")
            print("  4. Igual que el último día que operé")
            #print("  5. Cambio de driver (no implementado)")
            self.tipo = input("Seleccione una opción (0-6): ").strip()
            if self.tipo == "5":
                try:
                    shutil.rmtree(self.cache)
                    print("Caché purgada.")
                except Exception as e:
                    print(f"Error al purgar la caché: {e}")
            if self.tipo == "6":
                config["source"] =(config.get("source",0)+1) % len(sourceSource)
            if config.get("source",0)==1 and config.get("eodhd_key","") == "":
                eodhd_key = input("EOD Historical Data Key: ").strip()
                if eodhd_key:
                    config["eodhd_key"] = eodhd_key
                    with open("config.json", "w") as f:
                        json.dump(config, f)
            if config.get("source",0)==2 and config.get("polygon_key","") == "":
                polygon_key = input("Polygon.io Key: ").strip()
                if polygon_key:
                    config["polygon_key"] = polygon_key
                    with open("config.json", "w") as f:
                        json.dump(config, f)
        p["tipo"] = self.tipo
        self.sourceSource=sourceSource[config["source"]]

        if self.tipo == "4":
            self.tipo=config["tipo"]
            self.hora= config["hora"]
            self.apalancamiento= config["apalancamiento"]
        else:
            self.hora = None
            self.apalancamiento=None

        if self.tipo in ["1"]:
            """ # [2026-01-26] Quitado, para mejora
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
            """

            self.cash, self.posiciones = self._manual_capture_portfolio()

        if self.tipo in ["1", "2", "3", "4"]:
            # Ajusta la fecha de incio y fin
            today = pd.Timestamp.now().normalize()
            stoday = today.strftime("%Y-%m-%d")

            tipoB=False
            for p2 in self.p:
                if isinstance(self.p[p2], list):
                    tipoB=True
                    break

            if not tipoB:
                start=today - pd.Timedelta(days=(p["ring_size"]+ p["rlog_size"])* 8/5)  # 7/5 días por el margen de ordenes
                start= start.strftime("%Y-%m-%d")
                self.p["fecha_inicio"] = start
            self.p["fecha_fin"] = stoday

        # Pregunta si desea ver una gráfica
        self.verGrafica = False
        if self.tipo == "0":
            self.verGrafica = None
            while self.verGrafica not in [True, False]:
                respuesta = input("¿Deseas ver una gráfica de la simulación? (s/n): ").strip().lower()
                if respuesta == "s":
                    self.verGrafica = True
                elif respuesta == "n":
                    self.verGrafica = False

        # apalancamiento
        if not isinstance(self.p.get("apalancamiento"), (list)):
            print("\nApalancamiento: (un número entre 0.0 y 1.9) que representa el uso del cash.")
            print("Nota: El cash incluye el 50% de la expectativa de ventas y los dolares disponibles.")
            # print("Nota: Primerizos, empieza con 0.2 y ve subiendo poco a poco en sucesivos días a medida que compre.")
            print(" 0   No compres hoy")
            print(" 0.2 Usa el 20% del cash")
            print(" 1   Usar todo el dinero disponible")
            print(" 1.6 Un ligero apalancamiento dispara la rentabilidad, usalo cuando hayas simulado y tengas confianza en la estrategia")
            while self.apalancamiento is None or not (0 <= self.apalancamiento <= 1.9):
                try:
                    self.apalancamiento = float(input("Ingrese el apalancamiento: "))
                except ValueError:
                    print("Por favor, ingrese un número válido entre 0.0 y 1.9.")
            p["apalancamiento"] = self.apalancamiento

        if self.tipo in ["1", "2", "3"]:
            # check valid time format HH:MM
            while not self.hora or not self.hora.count(":") == 1 or not all(part.isdigit() for part in self.hora.split(":")) or not (0 <= int(self.hora.split(":")[0]) < 24) or not (0 <= int(self.hora.split(":")[1]) < 60):
                self.hora = input("\nA que hora US deseas entrar a operar? (Ej: 10:00 a 12:00) (HH:MM): ")
            # format hora to HH:MM
            self.hora = self.hora.strip()
            if len(self.hora) == 4:
                self.hora = "0" + self.hora
        
        # guardar en config.json
        if self.tipo in ["1","2","3"]:
            with open("config.json", "w") as f:
                config["hora"] = self.hora
                config["apalancamiento"] = self.apalancamiento
                config["tipo"] = self.tipo
                json.dump(config, f)
        #self.p=config
        self.p["polygon_key"] = config.get("polygon_key", "")
        self.p["eodhd_key"] = config.get("eodhd_key", "")
        self.p["source"] = config["source"]
        self.Source=sourceSource[config["source"]]

    def readTickersFromWikipedia(self):
        """ # Puesto como comentario [2026-01-27]
        # Leer la tabla de Wikipedia
        # url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        # tablas = read_html_like(self,url)
        # sp500 = tablas[0]  # La primera tabla es la que contiene la información

        # Obtener la columna de los símbolos/tickers
        # Aportación de @Tomeu
        #try:
        #    tickers = sp500['Symbol'].str.replace('.', '-').tolist()
        #except:
        #    print("Error al leer los tickers de Wikipedia. Usando pyroboadvisor.org como alternativa.")
        url = 'https://pyroboadvisor.org:443/index?numberIndex=0'
        resp = requests.get(url, verify=False)
        resp.raise_for_status()  # lanza excepción si hubo error HTTP
        data = resp.json()  # -> dict con name y codes
        self.marketName= data.get("name", "Unknown")
        tickers= data.get("codes", [])
        # sort 
        tickers.sort()
        self.tickers = tickers
        if self.p.get("source",0)==0:
            pass
        # else:
        #     from market.sourcePerDayPolygon import SourcePerDay
        #     self.sp= SourcePerDay(self.p)
        #     #self.tickers = self.sp.symbols

        #     self.sp.symbols = tickers
        #     self.sp.size = len(tickers)

        #self.source=Source
        """
        url = "https://pyroboadvisor.org:443/index?numberIndex=0"

        data = get_json_with_feedback(
            url,
            verify=False,
            max_attempts=5, 
            timeout=(25, 500)
        )

        self.marketName = data.get("name", "Unknown")
        tickers = data.get("codes", [])
        tickers.sort()
        self.tickers = tickers

    def readTickersFromEODHD(self,index=0):
        url="https://127.0.0.1:443/index?numberIndex="+str(index)
        resp = requests.get(url, verify=False)
        resp.raise_for_status()  # lanza excepción si hubo error HTTP

        data = resp.json()  # -> dict con name y codes

        name = data.get("name", "Unknown")
        codes = data.get("codes", [])

        # Guardar en el objeto (opcional, como en tu código original)
        self.tickers = codes
        self.marketName = name

    def readTickers(self,index=0):
        # if self.p["source"]==0:
        #     self.readTickersFromWikipedia()
        # elif self.p["source"]==1:
        self.readTickersFromEODHD(index)
        # elif self.p["source"]==2:
        #     from market.sourcePolygon import SourcePolygon
        #     self.Source=SourcePolygon
        #     self.sp= SourcePerDayPolygon(self.p)
        #     self.tickers = self.sp.symbols
        # else:
        #     print("Fuente de datos no válida")
        #     sys.exit()

    def prepare(self):
        p=self.p
        # if self.p.get("source",0)==0:
        self.source=self.Source(p,self.cache,
            lista_instrumentos=self.tickers,
            fecha_inicio=p["fecha_inicio"],
            fecha_fin=p["fecha_fin"],
            intervalo="1d"
        )

        self.sp=SourcePerDay(self.source)
        # else:
        #     self.sp.setDateRange(p["fecha_inicio"], p["fecha_fin"])

        p["tickers"]=self.sp.symbols

        simulator=Simulator(self.sp.symbols)
        simulator.money = p["money"]
        self.s=Strategy(p)
        ev=EstrategiaValuacion()
        self.simulator=simulator
        self.ev=ev
        # pos=self.tickers.index("FI")
        # if pos >=0:
        #     self.tickers[pos]="FISV"

    def simulate(self,signoMultiplexado=None):
        self.signoMultiplexado=signoMultiplexado
        simulator=self.simulator
        ev=self.ev
        while True:
            if signoMultiplexado is None:
                orders=self.s.open(self.sp.open)
            else:
                orders=self.s.open(self.sp.open, [sm(self.sp.current) for sm in signoMultiplexado])
            for order in orders["programBuy"]:
                if order["price"]==0:
                    continue
                simulator.programBuy(order["id"], order["price"], order["amount"])
            for order in orders["programSell"]:
                if order["price"]==0:
                    continue
                simulator.programSell(order["id"], order["price"], order["amount"])
            if hasattr(self.sp, "volume"):
                self.s.execute(self.sp.low,  self.sp.high, self.sp.close, self.sp.current, volume=self.sp.volume)
            else:
                self.s.execute(self.sp.low, self.sp.high, self.sp.close, self.sp.current)
            tasacion=simulator.execute(self.sp.low, self.sp.high, self.sp.close, self.sp.current)
            ev.add(self.sp.current, tasacion)
            hay=self.sp.nextDay()
            if not hay:
                break

        if self.verGrafica:
            apal = self.p.get("apalancamiento")
            extra = ""
            if apal is not None:
                pct = apal * 100
                if pct <= 100:
                    extra = f" ({pct:.0f}% uso del cash)"
                else:
                    extra = f" ({pct:.0f}% apalancamiento)"
            ev.print(self.s.name + extra)

    def _manual_capture_portfolio(self):
        opcion = ""
        while opcion not in ("1", "2"):
            print("\nManual:")
            print(" 1. Leer cartera desde archivo (manual.txt)")
            print(" 2. Introducir cartera manualmente")
            opcion = input("Seleccione (1-2): ").strip()

        if opcion == "1":
            return self._leer_manual_txt("manual.txt")
        return self._pedir_cartera_por_consola()

    def _leer_manual_txt(self, filepath: str):
        """
        - Ignora TODO lo que esté entre dos líneas delimitadoras de # (>=80 chars).
        - Se queda con la ÚLTIMA sección encontrada tras una línea de CASH (reinicia cartera al ver CASH).
        - Al final muestra lo leído y pide confirmación.
        """
        import os, sys, re

        if not os.path.exists(filepath):
            print(f"No existe el archivo {filepath}.")
            sys.exit()

        cash = None
        posiciones = {}

        cash_re = re.compile(
            r"^\s*(cash|efectivo|dinero)\s*[:=]?\s*([-+]?\d+(\.\d+)?)\s*$",
            re.I
        )

        def es_delimitador_hash(line: str) -> bool:
            s = line.strip()
            return len(s) >= 80 and set(s) == {"#"}

        def parse_position(line: str):
            parts = re.split(r"[,\s:;=]+", line.strip())
            if len(parts) < 2:
                return None
            sym = parts[0].strip().upper()
            if sym in ("CASH", "EFECTIVO", "DINERO"):
                return None
            try:
                qty = float(parts[1])
            except ValueError:
                return None
            return sym, qty

        ignorar = False
        with open(filepath, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue

                if es_delimitador_hash(line):
                    ignorar = not ignorar
                    continue
                if ignorar:
                    continue

                if line.startswith("#"):
                    continue

                m = cash_re.match(line)
                if m:
                    cash = float(m.group(2))
                    posiciones = {}  # nueva sección => “ignora ejemplo” si estaba antes
                    continue

                parsed = parse_position(line)
                if parsed:
                    sym, qty = parsed
                    posiciones[sym] = posiciones.get(sym, 0.0) + qty

        if cash is None:
            print(f"No se encontró una línea CASH válida en {filepath}.")
            sys.exit()
        if not posiciones:
            print(f"Se leyó CASH={cash}, pero no hay posiciones en {filepath}.")
            sys.exit()

        # Confirmación por terminal
        print("\nHe leído esto:")
        print(f"Cash: {cash}")
        for sym, qty in sorted(posiciones.items()):
            print(f"  {sym}: {qty}")
        ok = input("¿Es correcto? (s/n): ").strip().lower()
        if ok not in ("s", "si", "sí", "y", "yes"):
            print("Abortado. Corrige manual.txt o elige introducir manualmente.")
            sys.exit()

        return cash, posiciones


    def _pedir_cartera_por_consola(self):
        import sys

        while True:
            s = input("\nCash disponible (USD): ").strip().replace(",", "")
            try:
                cash = float(s)
                break
            except ValueError:
                print("Cash inválido. Ejemplo: 12345.67")

        posiciones = {}
        print("\nIntroduce posiciones. Escribe FIN para terminar.")
        while True:
            sym = input("Ticker: ").strip().upper()
            if sym in ("", "FIN", "END", "DONE", "SALIR", "0"):
                break
            if sym.startswith("#"):
                continue

            while True:
                q = input(f"Cantidad de {sym}: ").strip().replace(",", "")
                try:
                    qty = float(q)
                    break
                except ValueError:
                    print("Cantidad inválida. Ejemplo: 10")

            posiciones[sym] = posiciones.get(sym, 0.0) + qty

        if not posiciones:
            print("No se introdujeron posiciones. Abortando.")
            sys.exit()

        return cash, posiciones


    def manual(self, cash, portfolio):
        portfolio2 = [0] * len(self.sp.symbols)

        for symbol, num in portfolio.items():
            try:
                ind = self.sp.symbols.index(symbol)
            except ValueError:
                print(f"Símbolo {symbol} no encontrado en la lista de símbolos de entrenamiento. No emitirá señales de venta")
                continue
            portfolio2[ind] = num

        self.wait()
        self.s.set_portfolio(cash, portfolio2)

        if self.signoMultiplexado is None:
            orders = self.s.open(self.source.realTime(self.sp.symbols))
        else:
            orders = self.s.open(
                self.source.realTime(self.sp.symbols),
                [sm(self.sp.current) for sm in self.signoMultiplexado]
            )

        print("\nComprar:")
        for order in orders["programBuy"]:
            precio = round(order["price"], 2)
            if precio == 0:
                continue
            cantidad = int(round(order["amount"] / precio))
            print(f"{cantidad} acciones de {self.sp.symbols[order['id']]} a {precio:.2f}")

        print("\nVender:")
        for order in orders["programSell"]:
            precio = order["price"]
            if precio == 0:
                continue
            cantidad = order["amount"] / precio
            print(f"{cantidad:.4f} acciones de {self.sp.symbols[order['id']]} a {precio:.2f}")



    def completeTickersWithIB(self):
        """
        Completa la lista de tickers con los que están en la cuenta de IB.
        """
        if self.tipo in ["2","3"]: # IB
            from driver.driverIB import DriverIB as Driver
            d=Driver()
            puertos=[7496,7497,4001,4002]
            for p in puertos:
                try:
                    d.conectar(p)
                    break
                except:
                    pass
            if d.puerto is None:
                print("No se ha podido conectar a IB. Asegúrate de que TWS o IB Gateway estén en marcha y la API habilitada.")
                sys.exit()
            d.completeTicketsWithIB(self.tickers)
            self.d=d
        
    def autoIB(self):
        if self.d==None:
            from driver.driverIB import DriverIB as Driver
            self.d=Driver(7497)
            self.d.conectar()

        d=self.d

        cash= d.cash()
        portfolio=d.portfolio(self.sp.symbols)

        # pregunta por consola si desea operar en real, solo es posible una vez al día
        self.wait()

        rt=self.source.realTime(self.sp.symbols)

        self.s.set_portfolio(cash, portfolio)

        if self.signoMultiplexado is None:
            orders=self.s.open(rt)
        else:
            orders=self.s.open(rt,[sm(self.sp.current) for sm in self.signoMultiplexado])

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

        self.d.disconnect()

    def manualIB(self):
        if self.d==None:
            from driver.driverIB import DriverIB as Driver
            self.d=Driver(7497)
            self.d.conectar()
        d=self.d

        cash= d.cash()
        portfolio=d.portfolio(self.sp.symbols)

        self.wait()

        self.s.set_portfolio(cash, portfolio)

        if self.signoMultiplexado is None:
            orders=self.s.open(self.source.realTime(self.sp.symbols))
        else:
            orders=self.s.open(self.source.realTime(self.sp.symbols),[sm(self.sp.current) for sm in self.signoMultiplexado])

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
            time.sleep(1000)
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


if __name__ == "__main__":
    import socket
    import platform
    import os
    import subprocess

    def nombre_sin_guiones_y_derecha(nombre_completo: str) -> str:
        sin_guiones = nombre_completo.replace('-', '')
        # Paso 2: obtener la subcadena antes del primer punto (si existe)
        if '.' in sin_guiones:
            return sin_guiones.split('.', 1)[0]
        else:
            return sin_guiones



    print( nombre_sin_guiones_y_derecha(socket.gethostname()))


    import tempfile
    import os

    root = tempfile.gettempdir()          # Devuelve el "tmp dir" del sistema
    my_dir = os.path.join(root, "pyroboadvisor")
    os.makedirs(my_dir, exist_ok=True)
    print("Ruta personalizada:", my_dir)


def get_json_with_feedback(url, *, verify=False, max_attempts=4, timeout=(25, 300)):
    connect_s, read_s = timeout if isinstance(timeout, tuple) else (timeout, timeout)

    def _get_with_live_counter():
        out = {"resp": None, "err": None}

        def worker():
            try:
                out["resp"] = requests.get(url, verify=verify, timeout=(connect_s, read_s))
            except Exception as e:
                out["err"] = e

        th = threading.Thread(target=worker, daemon=True)
        th.start()

        t0 = time.time()
        while th.is_alive():
            elapsed = int(time.time() - t0)
            # “misma lógica” que wait(): se actualiza en la misma línea
            print(f"⏳ Esperando tickers... {elapsed}/{int(read_s)}s", end="\r", flush=True)
            time.sleep(1)

        # limpiar línea
        print(" " * 60, end="\r")

        if out["err"] is not None:
            raise out["err"]
        return out["resp"], time.time() - t0

    for attempt in range(1, max_attempts + 1):
        try:
            if attempt == 1:
                print(f"📡 Pidiendo tickers: {url} (Puede tardar varios minutos)", flush=True)
            else:
                print(f"📡 Reintento {attempt}/{max_attempts}: {url}", flush=True)

            resp, dt = _get_with_live_counter()
            resp.raise_for_status()

            size_kb = len(resp.content) / 1024
            print(f"✅ Tickers recibidos en {dt:.1f}s ({size_kb:.1f} KB)", flush=True)
            return resp.json()

        except requests.exceptions.ReadTimeout:
            print("⏳ Timeout. Reintentando...", flush=True)

        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}", flush=True)
            if attempt == max_attempts:
                raise
            print("🔁 Reintentando...", flush=True)

    raise RuntimeError("No se pudo descargar el JSON tras reintentos")
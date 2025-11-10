
from pyroboadvisor import PyRoboAdvisor
import pandas as pd
import shutil
import time

p={
    "fecha_inicio": "2018-01-01",
    "money": 100000,
    "numberStocksInPortfolio": 10,
    "orderMarginBuy": 0.005,  # margen de ordenes de compra y venta
    "orderMarginSell": 0.005,  # margen de ordenes de compra y venta
    "ring_size": 252,
    "rlog_size": [11,22,44],
    "skip_days": 252,
    "cabeza": 5,
    "prediccion": 1,

    "apalancamiento": 1.6,  
    "percentil": 90,
    "seeds": 1000,
    "multiploMantenimiento": 6,

    "har":1,
    "hretorno":1,
    "hrandom":1,
    
    "random_seed": 23,

    "key": "",
    "email": "",
    "b": True
}

def run():

    today = pd.Timestamp.now(tz='America/New_York').normalize()
    stoday = today.strftime("%Y-%m-%d")
    p["fecha_fin"]=stoday

    from download_us_money_supply import UsMoneySupply

    b=True
    if b:
        from download_us_money_supply import MakerUsMoneySupply
        mum=MakerUsMoneySupply("2018-01-01")
        usms=[]
        for meses in [6,12]:
            for percentil in [10,20,30,40,50,60,70,80,90]:
                usms.append(mum.get(meses,percentil).date2usms)
        p["signoMultiplexado"]=list(range(0,len(usms)))


    pra = PyRoboAdvisor(p,program={

        "email":"",
        "key":"",
        "hora":"", # Coloque una hora fija entre las 10:00 y las 12:00 
        "apalancamiento": 1.6,  # Si tu cuenta es de tipo efectivo/cash, debes poner aquí 1 

        "tipo":"3",
        "source":0,
    })
    try:
        shutil.rmtree(pra.cache)
    except:
        print("No cache folder")

    # pra.readTickersFromEODHD()
    pra.readTickersFromWikipedia()
    pra.completeTickersWithIB()  # Completa los tickers de IB que no están en el SP500, para que pueda venderlos
    pra.prepare()  # Prepara los datos y la estrategia


    if b:
        pra.simulate(signoMultiplexado=usms)
    else:
        pra.simulate()

    pra.automatizeOrders()


# --- Soporte de teclado no bloqueante ---
import sys, time
import pandas as pd
TARGET_HHMM = "05:00"
if sys.platform.startswith("win"):
    import msvcrt
    class KeyReader:
        def __enter__(self): return self
        def __exit__(self, *exc): pass
        def read(self):
            # Devuelve 'ENTER', 'ESC' o None
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch == '\r': return 'ENTER'
                if ch == '\x1b': return 'ESC'
            return None
else:
    import tty, termios, select
    class KeyReader:
        def __enter__(self):
            self.fd = sys.stdin.fileno()
            self.old = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)  # modo cbreak (no canónico)
            return self
        def __exit__(self, *exc):
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)
        def read(self):
            # Devuelve 'ENTER', 'ESC' o None
            r, _, _ = select.select([sys.stdin], [], [], 0)
            if r:
                ch = sys.stdin.read(1)
                if ch in ('\n', '\r'): return 'ENTER'
                if ch == '\x1b':       return 'ESC'
            return None

keys=KeyReader()

def wait(hoy=False):
    ahora = pd.Timestamp.now(tz='America/New_York')
    
    if not hoy:
        while True:
            print(ahora.strftime("%Y-%m-%d %H:%M:%S"),">","24:00", end="\r")
            ahora = pd.Timestamp.now(tz='America/New_York')
            # sleep 1 second
            time.sleep(1)
            if ahora.strftime("%H:%M") >= "23:58":
                break    
        time.sleep(120)  # wait 2 minutes

    # Arranque aleatorio
    import random
    from datetime import datetime, timedelta

    # Definir el rango de horas
    start_time = datetime.strptime("05:00", "%H:%M")
    end_time = datetime.strptime("08:00", "%H:%M")
    # Calcular la diferencia en minutos
    delta_minutes = int((end_time - start_time).total_seconds() // 60)
    # Elegir minutos aleatorios dentro del rango
    random_minutes = random.randint(0, delta_minutes)
    # Calcular la hora aleatoria
    random_time = start_time + timedelta(minutes=random_minutes)
    # Mostrar en formato HH:MM
    arranque=random_time.strftime("%H:%M")
    while True:

        print(ahora.strftime("%Y-%m-%d %H:%M:%S"),"<",arranque, end="\r")
        ahora = pd.Timestamp.now(tz='America/New_York')
        # sleep 1 second
        time.sleep(1)
        if ahora.strftime("%H:%M") >= arranque:
            break    

        k = keys.read()
        if k in ("ENTER",):
            print(f"\nEspera interrumpida por teclado ({k}).")
            break

if __name__ == "__main__":
    wait(hoy=True)
    while True:
        run()
        wait()

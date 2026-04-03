import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import warnings
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import random
import time
import threading

timeout=60*30

class StrategyClient:
    def __init__(self,p):
        self.verify_ssl = True  
        api_urls=["https://127.0.0.1:443","https://pyroboadvisor.org","https://pyroboadvisor.org:441","https://pyroboadvisor.org:442","https://pyroboadvisor.org:444","https://pyroboadvisor.org:445"]
        # if self.verify_ssl is False:
        #     print("WARNING: SSL verification is disabled. This is not recommended for production use.")
        #     # un numero random entre 2 y 4
        #     import random
        #     puerto=random.randint(2, 4)
        #     api_url="https://127.0.0.1:443"#+str(puerto)
        #     warnings.filterwarnings(
        #         "ignore",
        #         message="Unverified HTTPS request"
        #     )
        # self.api_url = api_url.rstrip("/")
        # Create requests session to handle ConnectionError
        i=0
        intento=0
        while True:
            intento+=1
            if i==0:
                self.verify_ssl = False
                warnings.filterwarnings(
                    "ignore",
                    message="Unverified HTTPS request"
                )
            else:
                self.verify_ssl = True
                warnings.filterwarnings(
                    "default",
                    message="Unverified HTTPS request"
                )
            api_url=api_urls[i]
            self.api_url = api_url.rstrip("/")
            self.requests_session = self._configure_requests_session(retries=3, backof_factor=0.5)
            self.session_id = None
            try:
                self.create_session(p)
                print(f"Connected to {self.api_url}")
                break
            except requests.exceptions.RequestException as e:
                if intento>10:
                    raise e
                time.sleep(2)
            # random i
            i=random.randint(0, len(api_urls)-1)

    def old_init(self,p):
        self.verify_ssl = False  
        api_url="https://pyroboadvisor.org"
        if self.verify_ssl is False:
            print("WARNING: SSL verification is disabled. This is not recommended for production use.")
            # un numero random entre 2 y 4
            import random
            puerto=random.randint(2, 4)
            api_url="https://127.0.0.1:443"#+str(puerto)
            warnings.filterwarnings(
                "ignore",
                message="Unverified HTTPS request"
            )
        self.api_url = api_url.rstrip("/")
        # Create requests session to handle ConnectionError
        self.requests_session = self._configure_requests_session(retries=3, backof_factor=0.5)
        self.session_id = None
        self.create_session(p)

    def _configure_requests_session(self, retries: int, backof_factor: float) -> requests.Session:
        session = requests.Session()
        retry = Retry(connect=retries, backoff_factor=backof_factor)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def create_session(self, config: dict):
        resp = self.requests_session.post(f"{self.api_url}/sessions", json={"config": config,"email": config["email"],
            "license_key": config["key"]},verify=self.verify_ssl, timeout=timeout)
        resp.raise_for_status()
        resp_json=resp.json()
        self.session_id = resp_json["session_id"]
        self.name = resp_json.get("strategy_name", "")
        if config.get("index",None) is not None:
            self.tickers = resp_json.get("tickers", [])

        return self.session_id

    """
    def open(self, open20,signoMultiplexado=None):
        if not self.session_id:
            raise Exception("Session not created")
        payload = {"open20": list(open20)}
        if signoMultiplexado is not None:
            payload["signoMultiplexado"]=signoMultiplexado
        resp = self.requests_session.post(f"{self.api_url}/sessions/{self.session_id}/open", json=payload, verify=self.verify_ssl,timeout=timeout )
        resp.raise_for_status()
        return resp.json()  # {'programSell': [...], 'programBuy': [...]}
    """

    def open(self, open20, signoMultiplexado=None):
        import requests, time

        if not self.session_id:
            raise Exception("Session not created")

        payload = {"open20": list(open20)}
        if signoMultiplexado is not None:
            payload["signoMultiplexado"] = signoMultiplexado

        max_attempts = 8
        base_wait = 2  # segundos

        for attempt in range(1, max_attempts + 1):
            try:
                # Solo mostramos mensajes desde el intento 2
                if attempt >= 2:
                    if attempt == 2:
                        print(f"[open] intento 1/{max_attempts} ha fallado (timeout). Reintentando...")
                    print(f"[open] intento {attempt}/{max_attempts} → {self.api_url}")

                resp = self.requests_session.post(
                    f"{self.api_url}/sessions/{self.session_id}/open",
                    json=payload,
                    verify=self.verify_ssl,
                    timeout=(10, timeout)
                )
                resp.raise_for_status()

                if attempt >= 2:
                    print("[open] OK")

                return resp.json()

            except requests.exceptions.ReadTimeout:
                wait_s = base_wait * (2 ** (attempt - 1))  # 2,4,8,16,32

                # Solo avisamos del timeout desde el intento 2 (porque el 1 se omite)
                if attempt >= 2:
                    print(f"[open] timeout. Reintentando en {wait_s}s...")

                time.sleep(wait_s)

            except requests.exceptions.RequestException as e:
                # Para errores no-timeout: si ocurren en el intento 1, saldrá sin log; si quieres log siempre, dímelo.
                if attempt >= 2:
                    print(f"[open] error: {e}")
                raise

        raise requests.exceptions.ReadTimeout(
            f"Timeout en open() tras {max_attempts} intentos (api={self.api_url})"
        )

    """
    def execute(self, low, high, close, date,volume=None):
        if not self.session_id:
            raise Exception("Session not created")
        payload = {
            "low": list(low),
            "high": list(high),
            "close": list(close),
            "date": str(date)  # Puede ser datetime.isoformat()
        }
        if volume!=None:
            payload["volume"]=list(volume)
        resp = self.requests_session.post(f"{self.api_url}/sessions/{self.session_id}/execute", json=payload, verify=self.verify_ssl, timeout=timeout)
        resp.raise_for_status()
        return resp.json()  # {'success': True}
    """

    def execute(self, low, high, close, date, volume=None):

        if not self.session_id:
            raise Exception("Session not created")

        payload = {
            "low": list(low),
            "high": list(high),
            "close": list(close),
            "date": str(date)
        }
        if volume is not None:
            payload["volume"] = list(volume)

        budgets = [15, 60, 180, 600]
        connect_s = 5
        last_err = None

        for idx, budget in enumerate(budgets, start=1):
            # intento 1: silencioso
            if idx == 1:
                try:
                    resp = self.requests_session.post(
                        f"{self.api_url}/sessions/{self.session_id}/execute",
                        json=payload,
                        verify=self.verify_ssl,
                        timeout=(connect_s, budget),
                    )
                    resp.raise_for_status()
                    return resp.json()
                except requests.exceptions.Timeout as e:
                    last_err = e
                except requests.exceptions.RequestException as e:
                    raise
                continue

            # intento 2+ : mensaje + contador
            if idx == 2:
                print(f"[execute] intento 1/{len(budgets)} ha fallado (timeout ~{budgets[0]}s).", flush=True)

            print(f"[execute] intento {idx}/{len(budgets)}: ejecutando ({budget}s)...", flush=True)

            result = {"resp": None, "err": None}

            def worker():
                try:
                    r = self.requests_session.post(
                        f"{self.api_url}/sessions/{self.session_id}/execute",
                        json=payload,
                        verify=self.verify_ssl,
                        timeout=(connect_s, budget),
                    )
                    r.raise_for_status()
                    result["resp"] = r
                except Exception as e:
                    result["err"] = e

            th = threading.Thread(target=worker, daemon=True)
            th.start()

            t0 = time.time()
            while th.is_alive():
                elapsed = int(time.time() - t0)
                if elapsed > budget:
                    break
                print(f"[execute] {idx}/{len(budgets)} esperando... {elapsed}/{budget}s", end="\r", flush=True)
                time.sleep(1)

            print(" " * 90, end="\r")
            th.join(timeout=1)

            if result["resp"] is not None:
                print(f"[execute] OK (intento {idx}/{len(budgets)})", flush=True)
                return result["resp"].json()

            err = result["err"] or last_err or requests.exceptions.ReadTimeout()
            last_err = err

            if isinstance(err, requests.exceptions.Timeout):
                print(f"[execute] timeout en intento {idx}/{len(budgets)}.", flush=True)
                continue

            if isinstance(err, requests.exceptions.HTTPError):
                code = getattr(err.response, "status_code", None)
                if code is not None and 500 <= code < 600:
                    print(f"[execute] HTTP {code} en intento {idx}/{len(budgets)}. Reintentando...", flush=True)
                    continue

            raise err

        raise requests.exceptions.ReadTimeout(
            f"[execute] abortado: no respondió tras {len(budgets)} intentos (15/60/180/600s). Último error: {last_err}"
        )



    def set_portfolio(self, cash, portfolio):
        if not self.session_id:
            raise Exception("Session not created")
        payload = {
            "cash": cash,
            "portfolio": portfolio
        }
        resp = self.requests_session.post(f"{self.api_url}/sessions/{self.session_id}/set_portfolio", json=payload, verify=self.verify_ssl, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    
    def get_index(self,id):
        if not self.session_id:
            raise Exception("Session not created")
        resp = self.requests_session.get(f"{self.api_url}/sessions/{self.session_id}/get_index/{id}", verify=self.verify_ssl, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    
    # def get_m2(self):
    #     if not self.session_id:
    #         raise Exception("Session not created")
    #     resp = self.requests_session.get(f"{self.api_url}/sessions/{self.session_id}/m2/", verify=self.verify_ssl, timeout=timeout)
    #     resp.raise_for_status()
    #     return resp.json()
    

    # def program_orders(self, orders, simulator):
    #     # Utiliza el mismo simulador que el bucle original
    #     for order in orders.get("programBuy", []):
    #         simulator.programBuy(order["id"], order["price"], order["amount"])
    #     for order in orders.get("programSell", []):
    #         simulator.programSell(order["id"], order["price"], order["amount"])

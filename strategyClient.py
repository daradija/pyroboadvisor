import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import warnings
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import random
import time

timeout=60*30

class StrategyClient:
    def __init__(self,p):
        self.verify_ssl = True  
        api_urls=["https://127.0.0.1:443","https://pyroboadvisor.org","https://pyroboadvisor.org:441","https://pyroboadvisor.org:442","https://pyroboadvisor.org:444"]
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
        self.name = resp_json.get("name", "")
        if config.get("index",None) is not None:
            self.tickers = resp_json.get("tickers", [])

        return self.session_id

    def open(self, open20,signoMultiplexado=None):
        if not self.session_id:
            raise Exception("Session not created")
        payload = {"open20": list(open20)}
        if signoMultiplexado is not None:
            payload["signoMultiplexado"]=signoMultiplexado
        resp = self.requests_session.post(f"{self.api_url}/sessions/{self.session_id}/open", json=payload, verify=self.verify_ssl,timeout=timeout )
        resp.raise_for_status()
        return resp.json()  # {'programSell': [...], 'programBuy': [...]}

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

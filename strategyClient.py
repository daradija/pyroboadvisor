import requests
import warnings
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

class StrategyClient:
    def __init__(self,p):
        self.verify_ssl = False  
        api_url="https://pyroboadvisor.org"
        if self.verify_ssl is False:
            api_url="https://localhost:443"
            warnings.filterwarnings(
                "ignore",
                message="Unverified HTTPS request"
            )
        self.api_url = api_url.rstrip("/")

        self.requests_session = self.configure_requests_session(retries=3, backof_factor=0.5)
        self.session_id = None


        self.create_session(p)



    def configure_requests_session(self, retries: int, backof_factor: float) -> requests.Session:
        session = requests.Session()
        retry = Retry(connect=retries, backoff_factor=backof_factor)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def create_session(self, config: dict):
        resp = requests.post(f"{self.api_url}/sessions", json={"config": config,"email": config["email"],
            "license_key": config["key"]},verify=self.verify_ssl)
        resp.raise_for_status()
        self.session_id = resp.json()["session_id"]
        return self.session_id

    def open(self, open20):
        if not self.session_id:
            raise Exception("Session not created")
        payload = {"open20": list(open20)}
        resp = requests.post(f"{self.api_url}/sessions/{self.session_id}/open", json=payload, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()  # {'programSell': [...], 'programBuy': [...]}

    def execute(self, low, high, close, date):
        if not self.session_id:
            raise Exception("Session not created")
        payload = {
            "low": list(low),
            "high": list(high),
            "close": list(close),
            "date": str(date)  # Puede ser datetime.isoformat()
        }
        resp = requests.post(f"{self.api_url}/sessions/{self.session_id}/execute", json=payload, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()  # {'success': True}

    def set_porfolio(self, cash, portfolio):
        if not self.session_id:
            raise Exception("Session not created")
        payload = {
            "cash": cash,
            "portfolio": portfolio
        }
        resp = requests.post(f"{self.api_url}/sessions/{self.session_id}/set_portfolio", json=payload, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()
    

    # def program_orders(self, orders, simulator):
    #     # Utiliza el mismo simulador que el bucle original
    #     for order in orders.get("programBuy", []):
    #         simulator.programBuy(order["id"], order["price"], order["amount"])
    #     for order in orders.get("programSell", []):
    #         simulator.programSell(order["id"], order["price"], order["amount"])

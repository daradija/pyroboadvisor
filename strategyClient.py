import requests
import warnings


class StrategyClient:
    def __init__(self,p):
        self.verify_ssl = True  
        api_url="https://pyroboadvisor.org"
        if self.verify_ssl is False:
            api_url="https://localhost:443"
            warnings.filterwarnings(
                "ignore",
                message="Unverified HTTPS request"
            )
        self.api_url = api_url.rstrip("/")
        self.session_id = None

        self.create_session(p)

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

    # En strategyClient.py, línea ~56, agregar debug:
    def set_profolio(self, cash, portfolio):
        if not self.session_id:
            raise Exception("Session not created")
        payload = {
            "cash": cash,
            "portfolio": portfolio
        }
        
        # DEBUG: Ver qué estamos enviando
        print(f"DEBUG - Enviando payload: {payload}")
        print(f"DEBUG - Cash type: {type(cash)}, value: {cash}")
        print(f"DEBUG - Portfolio type: {type(portfolio)}, length: {len(portfolio) if hasattr(portfolio, '__len__') else 'N/A'}")
        
        resp = requests.post(f"{self.api_url}/sessions/{self.session_id}/set_portfolio", 
                            json=payload, verify=self.verify_ssl)
        
        # DEBUG: Ver la respuesta
        print(f"DEBUG - Response status: {resp.status_code}")
        print(f"DEBUG - Response text: {resp.text}")
        
        resp.raise_for_status()
        return resp.json()

    # def program_orders(self, orders, simulator):
    #     # Utiliza el mismo simulador que el bucle original
    #     for order in orders.get("programBuy", []):
    #         simulator.programBuy(order["id"], order["price"], order["amount"])
    #     for order in orders.get("programSell", []):
    #         simulator.programSell(order["id"], order["price"], order["amount"])

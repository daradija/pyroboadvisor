import requests

class StrategyClient:
    def __init__(self,p):
        api_url="https://pyroboadvisor.org"
        self.api_url = api_url.rstrip("/")
        self.session_id = None
        self.create_session(p)

    def create_session(self, config: dict):
        resp = requests.post(f"{self.api_url}/sessions", json={"config": config,"email": config["email"],
            "license_key": config["key"]})
        resp.raise_for_status()
        self.session_id = resp.json()["session_id"]
        return self.session_id

    def open(self, open20):
        if not self.session_id:
            raise Exception("Session not created")
        payload = {"open20": list(open20)}
        resp = requests.post(f"{self.api_url}/sessions/{self.session_id}/open", json=payload)
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
        resp = requests.post(f"{self.api_url}/sessions/{self.session_id}/execute", json=payload)
        resp.raise_for_status()
        return resp.json()  # {'success': True}

    def program_orders(self, orders, simulator):
        # Utiliza el mismo simulador que el bucle original
        for order in orders.get("programBuy", []):
            simulator.programBuy(order["id"], order["price"], order["amount"])
        for order in orders.get("programSell", []):
            simulator.programSell(order["id"], order["price"], order["amount"])

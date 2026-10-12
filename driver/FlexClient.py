import datetime
import os
import time
import xml.etree.ElementTree as ET

import requests
from ib_insync import FlexReport

# El informe Flex debe tener:
#Sections:
#	- Cash Transactions 
#	  - Amount
#	  - Report Date
#	  - Currency
#	  - FX Rate To Base
#	  - Type
#	- Net Asset Value (NAV) in Base
#	  - Account ID
#	  - Report Date
#	  - Total
#Delivery Configuration:
#	- Format: XML
#	- Date Format: yyyyMMdd
#	- Breakout by Day? Yes
# NOTA: El token tiene validez de un año, asi que hay renovarlo para seguir recibiendo datos
class FlexClient:
    """Descarga un IBKR Flex Query y expone el historial de NAV y flujos de efectivo.
    Independiente del IB Gateway / TWS: solo necesita un token y un id de consulta."""

    BASE = "https://ndcdyn.interactivebrokers.com/AccountManagement/FlexWebService"
    # En el fichero XML encontraremos estas secciones
    NAV_TOPIC = "EquitySummaryByReportDateInBase" # NAV es Net Asset Value
    CASH_TOPIC = "CashTransaction"

    def __init__(self, token=None, query_id=None, retries=12, wait=5):
        self.token = token # Se obtiene de Flex Web Service Configuration
        self.query_id = query_id # Se obtiene al editar el informe Flex
        if not self.token or not self.query_id:
            raise ValueError("Faltan token o query_id para FlexClient")
        self.retries = retries
        self.wait = wait
        self._report = None          # cached: solo una descarga (Flex tiene limite de 10 descargas por hora)

    def fetch(self, force=False):
        """Descarga el informe Flex y lo devuelve como un objeto FlexReport."""
        if self._report is not None and not force:
            return self._report

        r = requests.get(f"{self.BASE}/SendRequest", params={"t": self.token, "q": self.query_id, "v": 3}, timeout=30)
        root = ET.fromstring(r.content)
        if root.findtext("Status") != "Success":
            raise RuntimeError(f"Flex SendRequest ha fallado: {root.findtext('ErrorCode')} {root.findtext('ErrorMessage')}")
        ref, url = root.findtext("ReferenceCode"), root.findtext("Url")

        for attempt in range(1, self.retries + 1):
            r = requests.get(url, params={"q": ref, "t": self.token, "v": 3}, timeout=60)
            root = ET.fromstring(r.content)
            if root.tag != "FlexStatementResponse":      
                report = FlexReport()
                report.data, report.root = r.content, root
                self._report = report
                return report
            code, msg = root.findtext("ErrorCode"), root.findtext("ErrorMessage")
            if code == "1019":
                print(f"Informe Flex no esta disponible (attempt {attempt}/{self.retries}), esperando {self.wait}s...")
                time.sleep(self.wait)
                continue
            raise RuntimeError(f"Flex GetStatementha fallado: {code} {msg}")
        raise TimeoutError("Informe Flex no esta disponible tras varios intentos")

    @staticmethod
    def _to_date(raw):
        raw = str(raw).strip()
        try:
            if raw[:8].isdigit():
                return datetime.datetime.strptime(raw[:8], "%Y%m%d").date()
            return datetime.datetime.strptime(raw[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    def nav_history(self):
        """{date: NAV in base currency} (agrupa todas las cuentas)."""
        nav = {}
        for r in self.fetch().extract(self.NAV_TOPIC, parseNumbers=False):
            d = self._to_date(getattr(r, "reportDate", ""))
            try:
                if d:
                    nav[d] = nav.get(d, 0.0) + float(r.total)
            except (TypeError, ValueError, AttributeError):
                continue
        return nav

    def cash_flows(self):
        """[(date, amount in base currency)] for entradas/salidas; [] si no hay datos en la seccion de Cash Transactions"""
        flows = []
        try:
            rows = self.fetch().extract(self.CASH_TOPIC, parseNumbers=False)
        except Exception:
            return flows
        for r in rows:
            if "deposit" not in str(getattr(r, "type", "")).lower():
                continue
            d = self._to_date(getattr(r, "reportDate", "") or getattr(r, "dateTime", ""))
            try:
                fx = float(getattr(r, "fxRateToBase", 1) or 1)
                if d:
                    flows.append((d, float(r.amount) * fx))
            except (TypeError, ValueError, AttributeError):
                continue
        return flows
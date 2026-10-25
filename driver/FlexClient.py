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

    def __init__(self, token=None, query_id=None, retries=15, wait=5, max_wait=150):
        self.token = token # Se obtiene de Flex Web Service Configuration
        self.query_id = query_id # Se obtiene al editar el informe Flex
        if not self.token or not self.query_id:
            raise ValueError("Faltan token o query_id para FlexClient")
        self.retries = retries
        self.wait = wait
        self.max_wait = max_wait     # la espera crece wait, 2*wait, ... hasta max_wait (unos 6 min en total por defecto)
        self._report = None          # cached: solo una descarga (Flex tiene limite de 10 descargas por hora)

    def fetch(self, force=False):
        """Descarga el informe Flex y lo devuelve como un objeto FlexReport."""
        if self._report is not None and not force:
            return self._report

        r = self._get(f"{self.BASE}/SendRequest", params={"t": self.token, "q": self.query_id, "v": 3}, timeout=30)
        root = ET.fromstring(r.content)
        if root.findtext("Status") != "Success":
            raise RuntimeError(f"Flex SendRequest ha fallado: {root.findtext('ErrorCode')} {root.findtext('ErrorMessage')}")
        ref, url = root.findtext("ReferenceCode"), root.findtext("Url")

        for attempt in range(1, self.retries + 1):
            # Si el host que devuelve IB (p.ej. gdcdyn) no resuelve, se usa el host base
            r = self._get(url, params={"q": ref, "t": self.token, "v": 3}, timeout=60,
                          fallback=f"{self.BASE}/GetStatement")
            root = ET.fromstring(r.content)
            if root.tag != "FlexStatementResponse":      
                report = FlexReport()
                report.data, report.root = r.content, root
                self._report = report
                return report
            code, msg = root.findtext("ErrorCode"), root.findtext("ErrorMessage")
            if code == "1019":   # el informe aún se está generando: los periodos largos pueden tardar minutos
                espera = min(self.wait * attempt, self.max_wait)
                print(f"Informe Flex no esta aun disponible, esperando {espera}s...")
                time.sleep(espera)
                continue
            raise RuntimeError(f"Flex GetStatementha fallado: {code} {msg}")
        raise TimeoutError("Informe Flex no esta disponible tras varios intentos")

    def _get(self, url, params, timeout, fallback=None, intentos=3):
        """GET con reintentos ante errores de red (DNS, conexión, timeout).
        Tras el primer fallo prueba `fallback` si se indica. Los errores no incluyen la URL para no mostrar el token."""
        urls = [url] if not fallback or fallback == url else [url, fallback]
        ultimo = None
        for intento in range(1, intentos + 1):
            for u in urls:
                try:
                    r = requests.get(u, params=params, timeout=timeout)
                    r.raise_for_status()
                    return r
                except requests.RequestException as e:
                    ultimo = f"{type(e).__name__} en {requests.utils.urlparse(u).hostname}"
                    print(f"Error de red con Flex ({ultimo}), intento {intento}/{intentos}")
            if intento < intentos:
                time.sleep(self.wait)
        raise ConnectionError(f"No se pudo conectar con Flex: {ultimo}")

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
        """{date: NAV in base currency} (agrupa todas las cuentas).
        Una misma fecha aparece en varios FlexStatement
        Se debe quedar con el valor del statement más reciente en lugar de sumarlos."""
        root = self.fetch().root
        statements = list(root.iter("FlexStatement")) or [root]
        statements.sort(key=lambda s: (s.get("toDate", ""), s.get("whenGenerated", "")))

        por_cuenta = {}
        for st in statements:
            for el in st.iter(self.NAV_TOPIC):
                d = self._to_date(el.get("reportDate", ""))
                try:
                    if d:
                        por_cuenta[(el.get("accountId", ""), d)] = float(el.get("total"))
                except (TypeError, ValueError):
                    continue

        nav = {}
        for (_, d), total in por_cuenta.items():
            nav[d] = nav.get(d, 0.0) + total
        return nav

    def cash_flows(self):
        """[(date, amount in base currency)] for entradas/salidas; [] si no hay datos en la seccion de Cash Transactions"""
        flows = []
        try:
            rows = self.fetch().extract(self.CASH_TOPIC, parseNumbers=False)
        except Exception:
            return flows
        for r in rows:
            # Con "Summary" activado, Flex añade filas resumen que duplicarían los flujos de detalle
            if str(getattr(r, "levelOfDetail", "DETAIL") or "DETAIL").upper() != "DETAIL":
                continue
            if str(getattr(r, "currency", "")).upper() == "BASE_SUMMARY":
                continue
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
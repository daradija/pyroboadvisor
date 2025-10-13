#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
m2_numpy_con_publicacion.py

Descarga M2 (M2SL) desde FRED a partir de una fecha "desde" y devuelve/guarda
un array estructurado de NumPy con 3 columnas:
  - fecha     (datetime64[D])  -> mes del dato (FRED)
  - publicado (datetime64[D])  -> día del release H.6 que lo publica
  - M2        (float64)        -> miles de millones de USD, SA

Requisitos: requests, numpy
  pip install requests numpy

Uso (CLI):
  export FRED_API_KEY="TU_API_KEY"
  python m2_numpy_con_publicacion.py --desde 2019-09-01 --out m2.csv
"""

from __future__ import annotations
import os
import sys
import argparse
from datetime import date, datetime, timedelta
import requests
import numpy as np

# -------------------------- utilidades de fecha ---------------------------

def _parse_desde(desde: str) -> date:
    """
    Acepta formatos comunes y normaliza al primer día del mes si solo hay año-mes.
    """
    formatos = ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%Y-%m", "%Y/%m", "%d-%m-%Y")
    for fmt in formatos:
        try:
            dt = datetime.strptime(desde, fmt)
            if "%d" not in fmt:
                dt = dt.replace(day=1)
            return dt.date()
        except ValueError:
            continue
    raise ValueError("Formato de fecha no válido. Ej.: '2019-09-01' o '01/09/2019'.")

def _last_day_of_month(d: date) -> date:
    return (d.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

# ------------------------------ FRED helpers -----------------------------

_FRED = "https://api.stlouisfed.org/fred"

def _get_release_id_for_series(series_id: str, api_key: str) -> int:
    """
    Devuelve el release (H.6) que publica la serie.
    Endpoint correcto: /series/release (SINGULAR).
    """
    url = f"{_FRED}/series/release"
    p = {"series_id": series_id, "api_key": api_key, "file_type": "json"}
    r = requests.get(url, params=p, timeout=30)
    r.raise_for_status()
    rels = r.json().get("releases", [])
    if not rels:
        raise RuntimeError(f"No se encontraron releases para {series_id}: {r.text[:200]}")
    rid = rels[0].get("id") or rels[0].get("release_id")
    if rid is None:
        raise RuntimeError(f"Respuesta inesperada en series/release: {rels[0]}")
    return int(rid)

def _get_release_dates(
    release_id: int, api_key: str, start: date | None = None, end: date | None = None
) -> list[date]:
    """Devuelve las fechas de publicación (release dates) para el release dado."""
    url = f"{_FRED}/release/dates"
    p = {"release_id": release_id, "api_key": api_key, "file_type": "json"}
    if start:
        p["start"] = start.isoformat()
    if end:
        p["end"] = end.isoformat()
    r = requests.get(url, params=p, timeout=30)
    r.raise_for_status()
    items = r.json().get("release_dates", [])
    dates = [datetime.strptime(it["date"][:10], "%Y-%m-%d").date() for it in items]
    dates.sort()
    return dates

def _get_observations_M2(start: date, api_key: str):
    """
    Observaciones M2SL desde start.
    Devuelve dos arrays Python: fechas (date) y valores (float con NaN).
    """
    url = f"{_FRED}/series/observations"
    p = {
        "series_id": "M2SL",
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start.isoformat(),
    }
    r = requests.get(url, params=p, timeout=30)
    r.raise_for_status()
    obs = r.json().get("observations", [])
    fechas = []
    valores = []
    for o in obs:
        fechas.append(datetime.strptime(o["date"][:10], "%Y-%m-%d").date())
        valores.append(np.nan if o["value"] == "." else float(o["value"]))
    return np.array(fechas, dtype=object), np.array(valores, dtype="f8")

# -------------------------- función principal ----------------------------

def m2_numpy_con_publicacion(desde: str, api_key: str, dropna: bool = True) -> np.ndarray:
    """
    Devuelve un ndarray estructurado con:
      'fecha'     -> datetime64[D]  (mes del dato)
      'publicado' -> datetime64[D]  (día del H.6 que lo publica)
      'M2'        -> float64

    Para cada mes, asigna la PRIMERA fecha de release estrictamente posterior
    al último día de ese mes. Si aún no existe (último dato), pone NaT.
    """
    inicio = _parse_desde(desde)

    # 1) Dato M2
    fechas_obj, M2 = _get_observations_M2(inicio, api_key)

    # 2) Release dates del H.6
    rid = _get_release_id_for_series("M2SL", api_key)
    hoy = date.today()
    rel_dates = _get_release_dates(
        rid,
        api_key,
        start=inicio - timedelta(days=5),  # margen
        end=hoy + timedelta(days=62),      # capturar la próxima publicación
    )

    # 3) Mapear cada fin de mes -> primer release posterior
    publicados: list[date | None] = []
    i = 0
    for f in fechas_obj:
        fin_mes = _last_day_of_month(f)
        while i < len(rel_dates) and rel_dates[i] <= fin_mes:
            i += 1
        pub = rel_dates[i] if i < len(rel_dates) else None  # puede ser None para el último mes
        publicados.append(pub)

    # 4) Construir ndarray estructurado
    fechas_np = np.array(fechas_obj, dtype="datetime64[D]")
    publicados_np = np.array(
        [np.datetime64(p) if p else np.datetime64("NaT") for p in publicados],
        dtype="datetime64[D]"
    )

    if dropna:
        mask = ~np.isnan(M2)
        fechas_np = fechas_np[mask]
        publicados_np = publicados_np[mask]
        M2 = M2[mask]

    out = np.empty(
        fechas_np.shape[0],
        dtype=[("fecha", "datetime64[D]"), ("publicado", "datetime64[D]"), ("M2", "f8")],
    )
    out["fecha"] = fechas_np
    out["publicado"] = publicados_np
    out["M2"] = M2
    return out

# ------------------------------- CLI -------------------------------------

def _to_csv(arr: np.ndarray, path: str) -> None:
    """Guarda el array estructurado a CSV (tres columnas)."""
    # convertir fechas a str ISO
    fecha = arr["fecha"].astype("datetime64[D]").astype("datetime64[s]").astype(object)
    publicado = arr["publicado"].astype("datetime64[D]").astype("datetime64[s]").astype(object)

    with open(path, "w", encoding="utf-8") as f:
        f.write("fecha,publicado,M2\n")
        for d, p, v in zip(fecha, publicado, arr["M2"]):
            d_str = "" if d is np.datetime64("NaT") else str(d)[:10]
            p_str = "" if p is np.datetime64("NaT") else str(p)[:10]
            f.write(f"{d_str},{p_str},{v:.6f}\n")

def percentile_rank(a, x, method='rank'):
    """
    a: array de datos
    x: valor (o array de valores) del que quieres el percentil
    method:
      - 'strict' -> % de valores < x
      - 'weak'   -> % de valores <= x
      - 'rank'   -> % de valores < x + 0.5 * % de iguales a x (por defecto)
      - 'mean'   -> igual que 'rank'
    """
    a = np.asarray(a, dtype=float)
    x = np.asarray(x, dtype=float)
    a = a[~np.isnan(a)]
    if a.size == 0:
        raise ValueError("array vacío tras eliminar NaNs")

    a.sort()
    n = a.size

    if method == 'strict':
        k = np.searchsorted(a, x, side='left')
    elif method == 'weak':
        k = np.searchsorted(a, x, side='right')
    elif method in ('rank', 'mean'):
        k_left  = np.searchsorted(a, x, side='left')
        k_right = np.searchsorted(a, x, side='right')
        k = 0.5 * (k_left + k_right)
    else:
        raise ValueError("method debe ser 'strict', 'weak', 'rank' o 'mean'")

    return (np.asarray(k) / n) * 100.0



class MakerUsMoneySupply:
    def __init__(self,sdate):
        # self.user(sdate)
        self.server()

    def server(self):
        url="https://pyroboadvisor.org/m2"
        resp = requests.get(url, verify=False)
        resp.raise_for_status()  # lanza excepción si hubo error HTTP

        data = resp.json()  # -> dict con name y codes

        # Supongamos que resp.json() ya lo convertiste a un np.array con dtype compuesto
        arr = np.array(list(zip(data["fecha"], data["publicado"], data["M2"])),
                    dtype=[('fecha','datetime64[D]'),
                            ('publicado','datetime64[D]'),
                            ('M2','f8')])

        # ahora DataFrame:
        self.datos=arr
        
    def user(self,sdate):
        # Ejemplo de uso:
        api_key = "pon tu API key de FRED"
        sdate = (datetime.strptime(sdate, "%Y-%m-%d") - timedelta(days=365)).strftime("%Y-%m-%d")
        self.datos = m2_numpy_con_publicacion(sdate, api_key)

    def get(self,meses,percentil_filtro):
        return UsMoneySupply(self.datos,meses,percentil_filtro)


class UsMoneySupply:
    def __init__(self,datos,meses,percentil_filtro):
        self.datos=datos
        self.meses=meses
        self.percentil_filtro=percentil_filtro
        # "01/12/2018"
        # Substrae 1 año a sdate


        # print(self.datos)



    def date2usms_exp(self, fecha: date) -> list[float]:
        """Convierte una fecha a su correspondiente valor de M2."""
        sfecha = fecha.strftime("%Y-%m-%d")
        anterior = None
        acumulado = 0.0
        total = 0
        for d in self.datos:
            auxFecha=d[1]
            # numpy.datetime64 to str
            sauxFecha=str(auxFecha)[:10]
            if sauxFecha < sfecha:
                # calculas promedio
                if anterior is not None:
                    alfa=0.99
                    acumulado=acumulado*alfa+d[2]-anterior
                    total=total*alfa+1
                anterior=d[2]
            else:
                promedio=acumulado/total 
                return [d[2]-anterior - promedio]
        return [0.0]
    
    def date2usms(self, fecha: date) -> list[float]:
        """Por percentil"""
        sfecha = fecha.strftime("%Y-%m-%d")
        anterior = None
        acumulado = []
        last=0
        for id,d in enumerate(self.datos):
            auxFecha=d[1]
            # numpy.datetime64 to str
            sauxFecha=str(auxFecha)[:10]
            if sauxFecha < sfecha:
                # calculas promedio
                if anterior is not None:
                    acumulado.append(d[2]-anterior)
            else:
                # per=percentile_rank(np.array(acumulado[-12:]), d[2]-anterior) 
                # return [per-30]
                break
            if anterior is not None and len(acumulado)>=self.meses:
                # if id==len(self.datos)-1:
                #     print("ultimo")
                last=percentile_rank(np.array(acumulado[-self.meses:]), d[2]-anterior) -self.percentil_filtro
            anterior=d[2]

        return float(last)

# anterior=None
# for d in datos:
#     if anterior is not None:
#         delta=d[2] - anterior
#         print(d[1],delta)
#     anterior = d[2]

if __name__ == "__main__":
    ums=UsMoneySupply("2021-01-01",6,20)
    print(ums.datos[-10:])
    stoday=datetime.now()
    sdate="2025-09-24"
    date=datetime.strptime(sdate, "%Y-%m-%d")
    print(ums.date2usms(date))
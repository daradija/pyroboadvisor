# Helper para gestionar la configuración

import pandas as pd
import os

def parse_config(path):
    config = {}
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.split('#')[0].strip()
    return config

def get_parameters(config_path):
    today = pd.Timestamp.now().normalize()
    stoday = today.strftime("%Y-%m-%d")
    use_config = False
    p = {}

    if os.path.exists(config_path):
        try:
            config = parse_config(config_path)
            p = {
                "fecha_inicio": config.get("fecha_inicio", "2019-01-01"),
                "fecha_fin": stoday,
                "money": float(config.get("money", 100000)),
                "numberStocksInPortfolio": int(config.get("numberStocksInPortfolio", 10)),
                "orderMarginBuy": float(config.get("orderMarginBuy", 0.005)),
                "orderMarginSell": float(config.get("orderMarginSell", 0.005)),
                "apalancamiento": float(config.get("apalancamiento", 1.7)),
                "ring_size": int(config.get("ring_size", 252)),
                "rlog_size": int(config.get("rlog_size", 22)),
                "cabeza": int(config.get("cabeza", 5)),
                "seeds": int(config.get("seeds", 100)),
                "percentil": int(config.get("percentil", 95)),
                "prediccion": int(config.get("prediccion", 1)),
                "key": config.get("key", ""),
                "email": config.get("email", ""),
                "tipo": int(config.get("modo", 0)),
                "hora": config.get("hora", "10:00"),
                "puerto": int(config.get("puerto", 7467)),
                "desatendido": True,
                "source": int(config.get("source") or 0),
                "eodhd_key": config.get("eodhd_key", ""),
                "polygon_key": config.get("polygon_key", ""),
                "har": int(config.get("har", 1)),
                "hretorno": int(config.get("hretorno", 1)),
                "hrandom": int(config.get("hrandom", 1)),
                "multiploMantenimiento": int(config.get("multiploMantenimiento", 6)),
                "b": config.get("b", "True").lower() in ("true", "1", "yes"),                
            }
            use_config = True
        except Exception as e:
            print(f"Error parsing config: {e}")
            use_config = False

    if not use_config:
        p = {
            "fecha_inicio": "2019-01-01",
            "fecha_fin": stoday,
            "money": 100000,
            "numberStocksInPortfolio": 10,
            "orderMarginBuy": 0.005,
            "orderMarginSell": 0.005,
            "apalancamiento": 1.7,
            "ring_size": 252,
            "rlog_size": 22,
            "cabeza": 5,
            "seeds": 1000,
            "percentil": 90,
            "prediccion": 1,
            "har":1,
            "hretorno":1,
            "hrandom":1,
            "multiploMantenimiento": 6,
            "key": "",
            "email": "",
            "puerto": 7467,
            "desatendido": False,
            "source": 0,
            "eodhd_key": "",
            "polygon_key": "",
            "b": True,
        }
    return p
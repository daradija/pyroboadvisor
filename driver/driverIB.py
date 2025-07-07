"""
Driver para Interactive Brokers usando IB Gateway
Compatible con PyroboAdvisor trading system

IMPORTANTE: Para evitar conflictos con el event loop en macOS + Python 3.9+:
1. Importar y conectar este driver ANTES que otras librerías de mercado
2. Usar importaciones diferidas para pandas, numpy, etc.
3. Mantener conexión activa durante toda la sesión
"""

import asyncio
import logging
import time
import sys
import platform
import math
import pytz
import datetime
from typing import List, Optional, Dict, Any
from ib_insync import IB, Stock, Order, MarketOrder, LimitOrder, Contract, util

# Configurar logging para ib_insync
logging.getLogger('ib_insync').setLevel(logging.WARNING)

# Fix para macOS + Python 3.9+
if platform.system() == 'Darwin' and sys.version_info >= (3, 9):
    try:
        import nest_asyncio
        nest_asyncio.apply()
        
        class MacOSEventLoopPolicy(asyncio.DefaultEventLoopPolicy):
            def new_event_loop(self):
                loop = super().new_event_loop()
                original_close = loop.close
                
                def patched_close():
                    try:
                        original_close()
                    except (AttributeError, RuntimeError):
                        pass
                
                loop.close = patched_close
                return loop
        
        asyncio.set_event_loop_policy(MacOSEventLoopPolicy())
        
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'nest-asyncio'])
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except Exception:
            pass

class DriverIB:
    """
    Driver para operar con Interactive Brokers a través de IB Gateway
    Compatible con la interfaz de PyroboAdvisor
    
    NOTAS DE USO:
    - Conectar ANTES de importar librerías de mercado (pandas, numpy, etc.)
    - En macOS, se aplican automáticamente los fixes para asyncio
    - Usar Paper Trading (puerto 7497) para pruebas
    """
    
    def __init__(self, puerto: int = 7497, host: str = "127.0.0.1", client_id: int = 1, account: str = ""):
        """
        Inicializa el driver de Interactive Brokers
        
        Args:
            puerto: Puerto del IB Gateway (7497=paper, 7496=live)
            host: IP del IB Gateway (por defecto localhost)
            client_id: ID único del cliente
            account: Número de cuenta IB (requerido para live)
        """
        self.host = host
        self.puerto = puerto
        self.client_id = client_id
        self.account = account
        self.ib = None
        self.connected = False
        self.is_paper = puerto == 7497
    
    def conectar(self) -> bool:
        """
        Establece conexión con IB Gateway
        
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            if platform.system() == 'Darwin':
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                except (RuntimeError, AttributeError):
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            
            self.ib = IB()
            timeout = 20 if platform.system() == 'Darwin' else 10
            self.ib.connect(self.host, self.puerto, clientId=self.client_id, timeout=timeout)
            self.connected = True
            
            if not self.ib.isConnected():
                self.connected = False
                return False
            
            accounts = self.ib.managedAccounts()
            if accounts:
                if not self.account:
                    self.account = accounts[0]
                elif self.account not in accounts:
                    self.account = accounts[0]
            
            return True
            
        except Exception as e:
            print(f"Error conectando: {e}")
            self.connected = False
            return False
    
    def profolio(self, symbols: List[str]) -> List[float]:
        """
        Obtiene las posiciones actuales del portfolio
        
        Args:
            symbols: Lista de símbolos
            
        Returns:
            List[float]: Lista de cantidades por símbolo
        """
        if not self.connected:
            return [0.0] * len(symbols)
        
        try:
            ps = self.ib.portfolio()
            r = [0] * len(symbols)
            
            for p in ps:
                symbol = p.contract.symbol 
                position = p.position 
                if position < 1:
                    continue
                marketPrice = p.marketPrice
                print(f"Symbol: {symbol}, Position: {position}, Market Price: {marketPrice}")
                if symbol in symbols:
                    r[symbols.index(symbol)] = position 
            
            return r
            
        except Exception as e:
            print(f"Error portfolio: {e}")
            return [0.0] * len(symbols)
    
    def cash(self) -> float:
        """
        Obtiene el efectivo disponible
        
        Returns:
            float: Cantidad de efectivo disponible
        """
        if not self.connected:
            return 0.0
        
        try:
            account = self.ib.accountSummary()
            for a in account:
                if a.tag == "TotalCashValue":
                    print(f"Total Cash Value: {a.value} {a.currency}")
                    if a.currency == "USD":
                        return float(a.value)
            
            print("No se encontró efectivo USD")
            return 0.0
            
        except Exception as e:
            print(f"Error cash: {e}")
            return 0.0
    
    def clearOrders(self) -> bool:
        """
        Cancela todas las órdenes pendientes
        
        Returns:
            bool: True si se cancelaron correctamente
        """
        if not self.connected:
            return False
        
        try:
            trades = self.ib.reqOpenOrders()
            self.ib.sleep(1)

            for trade in trades:
                oid = trade.order.orderId
                status = trade.orderStatus.status
                if status not in ('Cancelled', 'Filled'):
                    print(f"Cancelling order {oid}")
                    self.ib.cancelOrder(trade.order)
            
            return True
            
        except Exception as e:
            print(f"Error clearOrders: {e}")
            return False
    
    def buy_limit(self, symbol: str, units: int, limit_price: float) -> Optional[int]:
        """
        Coloca una orden LMT (limit) BUY de `units` acciones de `symbol`
        a un precio máximo de `limit_price`. Nunca salta a mercado.
        Devuelve el orderId.
        """
        if not self.connected:
            return None
        
        try:
            contract = self.createContract(symbol)
            order = LimitOrder('BUY', units, limit_price)
            trade = self.ib.placeOrder(contract, order)
            self.ib.sleep(1)  
            print(f"[BUY-LMT] {units} {symbol} @ {limit_price}")
            
            if trade and trade.order:
                return trade.order.orderId
            return None
            
        except Exception as e:
            print(f"Error buy_limit: {e}")
            return None

    def sell_limit(self, symbol: str, units: float, limit_price: float) -> Optional[int]:
        """
        Coloca una orden LMT (limit) SELL de `units` acciones de `symbol`
        a un precio mínimo de `limit_price`. Nunca salta a mercado.
        Devuelve el orderId.
        """
        if not self.connected:
            return None
        
        try:
            contract = self.createContract(symbol)
            int_units = math.floor(units)
            limit_price = round(limit_price, 2)
            order = LimitOrder('SELL', int_units, limit_price)
            trade = self.ib.placeOrder(contract, order)
            self.ib.sleep(1)  
            print(f"[SELL-LMT] {int_units} {symbol} @ {limit_price}")
            
            if trade and trade.order:
                return trade.order.orderId
            return None
            
        except Exception as e:
            print(f"Error sell_limit: {e}")
            return None

    def createContract(self, symbol: str) -> Contract:
        """
        Crea un contrato para el símbolo especificado
        """
        contract = Contract()
        contract.symbol = symbol
        contract.secType = 'STK'
        
        now = datetime.datetime.now(pytz.timezone('US/Eastern'))
        contract.exchange = "SMART" if now.hour < 16 else "OVERNIGHT"
        
        if symbol == "META":
            contract.primaryExchange = "NASDAQ"

        contract.currency = 'USD'
        return contract
    
    def get_market_data(self, symbols: List[str]) -> Dict[str, float]:
        """
        Obtiene datos de mercado en tiempo real
        
        Args:
            symbols: Lista de símbolos
            
        Returns:
            Dict[str, float]: Diccionario con precios actuales
        """
        if not self.connected:
            return {}
        
        try:
            prices = {}
            
            for symbol in symbols:
                try:
                    contract = self.createContract(symbol)
                    self.ib.reqMktData(contract, '', False, False)
                    time.sleep(0.1)
                    
                    ticker = self.ib.ticker(contract)
                    
                    if ticker and ticker.marketPrice():
                        prices[symbol] = float(ticker.marketPrice())
                    else:
                        prices[symbol] = 0.0
                    
                    self.ib.cancelMktData(contract)
                    
                except Exception:
                    prices[symbol] = 0.0
            
            return prices
            
        except Exception:
            return {}
    
    def disconnect(self):
        """
        Desconecta del IB Gateway con limpieza especial para macOS
        """
        if self.connected and self.ib:
            try:
                if platform.system() == 'Darwin':
                    try:
                        self.clearOrders()
                        time.sleep(0.5)
                    except Exception:
                        pass
                
                self.ib.disconnect()
                self.connected = False
                
            except Exception:
                self.connected = False
    
    def __del__(self):
        """
        Destructor mejorado para asegurar desconexión limpia
        """
        try:
            if hasattr(self, 'connected') and self.connected:
                self.disconnect()
        except Exception:
            # Ignorar errores en el destructor para evitar problemas
            # en el shutdown del programa
            pass
    
    def health_check(self) -> bool:
        """
        Verifica el estado de la conexión y la salud del sistema
        
        Returns:
            bool: True si todo está funcionando correctamente
        """
        if not self.connected or not self.ib:
            return False
        
        try:
            if not self.ib.isConnected():
                self.connected = False
                return False
            
            accounts = self.ib.managedAccounts()
            if not accounts:
                return False
            
            try:
                self.cash()
                return True
            except Exception:
                return False
            
        except Exception:
            return False
    
    def system_info(self):
        """
        Muestra información del sistema y configuración
        """
        print(f"SO: {platform.system()}")
        print(f"Python: {sys.version}")
        print(f"IB Gateway: {self.host}:{self.puerto}")
        print(f"Modo: {'Paper' if self.is_paper else 'Live'}")
        print(f"Conectado: {'Si' if self.connected else 'No'}")
        
        if self.connected:
            print(f"Cuenta: {self.account}")
            cash = self.cash()
            print(f"Efectivo: ${cash:,.2f}")


# Ejemplo de uso correcto
if __name__ == "__main__":
    """
    Ejemplo de uso correcto del DriverIB
    """
    print("Ejemplo de uso del DriverIB")
    
    # 1. Crear instancia (Paper Trading por defecto)
    d = DriverIB(puerto=7497, client_id=1)
    
    # 2. Mostrar información del sistema
    d.system_info()
    
    # 3. Conectar
    if d.conectar():
        # 4. Verificar salud
        if d.health_check():
            print("Driver listo para operar")
            
            # 5. Ejemplo de operaciones básicas
            try:
                # Obtener efectivo
                cash = d.cash()
                print(f"Efectivo disponible: ${cash:,.2f}")
                
                # Limpiar órdenes
                d.clearOrders()
                
                # Obtener posiciones (ejemplo con algunas acciones)
                symbols = ['AAPL', 'GOOGL', 'MSFT']
                positions = d.profolio(symbols)
                for i, symbol in enumerate(symbols):
                    print(f"{symbol}: {positions[i]}")
                
                # Obtener precios (ejemplo)
                prices = d.get_market_data(['AAPL'])
                if 'AAPL' in prices:
                    print(f"AAPL: ${prices['AAPL']:.2f}")
                
            except Exception as e:
                print(f"Error en operaciones: {e}")
        
        # 6. Desconectar
        d.disconnect()
    else:
        print("No se pudo conectar con IB Gateway")
        print("Asegúrate de que IB Gateway esté ejecutándose en el puerto 7497")

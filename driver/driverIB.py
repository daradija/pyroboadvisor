from ib_insync import IB, LimitOrder, Contract
import pytz
import datetime
import time
import math

class DriverIB:
    def __init__(self):
        self.ib = IB()
        self.puerto=None

    def conectar(self,puerto):
        self.ib.connect('127.0.0.1', puerto, clientId=1)
        self.puerto=puerto

    def disconnect(self):
        if self.ib is not None:
            self.ib.disconnect()
            self.ib = None

    def portfolio(self,symbols):
        ps=self.ib.portfolio()
        r=[0]*len(symbols)
        for p in ps:
            symbol = p.contract.symbol 
            position = p.position 
            if position<1:
                continue
            marketPrice=p.marketPrice
            print(f"Symbol: {symbol}, Position: {position}, Market Price: {marketPrice}")
            if symbol in symbols:
                r[symbols.index(symbol)] = position 
        return r
    
    def completeTicketsWithIB(self,tickers):
        ps=self.ib.portfolio()
        for p in ps:
            symbol = p.contract.symbol
            if not symbol in tickers:
                print(f"Adding {symbol} to tickers")
                tickers.append(symbol)
                
    def cash(self):
        account=self.ib.accountSummary()
        for a in account:
            if a.tag=="CashBalance":
                print(f"Cash Balance: {a.value} {a.currency}")
                if a.currency == "USD":
                    return float(a.value)
            if a.tag=="TotalCashBalance":
                print(f"Total Cash Balance: {a.value} {a.currency}")
                if a.currency == "USD":
                    return float(a.value)
            if a.tag == "TotalCashValue":
                print(f"Total Cash Value: {a.value} {a.currency}")
                if a.currency == "USD":
                    return float(a.value)
        print("No se encontró efectivo en USD en la cuenta.")
        return 0.0
    
    def clearOrders(self):
        # 1) Solicita las órdenes abiertas y deja que el event loop las procese
        trades = self.ib.reqOpenOrders()
        self.ib.sleep(1)

        # 2) Recorre sólo las órdenes cuyo estado no sea 'Cancelled' ni 'Filled'
        for trade in trades:
            oid = trade.order.orderId
            status = trade.orderStatus.status
            if status not in ('Cancelled', 'Filled'):
                print(f"Cancelling order {oid} (status was {status})")
                self.ib.cancelOrder(trade.order)
            else:
                print(f"Skipping order {oid} (already {status})")



    def buy_limit(self, symbol: str, units: int, limit_price: float) -> int:
            """
            Coloca una orden LMT (limit) BUY de `units` acciones de `symbol`
            a un precio máximo de `limit_price`. Nunca salta a mercado.
            Devuelve el orderId.
            """
            contract = self.createContract(symbol)
            order = LimitOrder('BUY', units, limit_price)
            self.ib.placeOrder(contract, order)
            self.ib.sleep(1)  
            print(f"[BUY-LMT] {units} {symbol} @ {limit_price}")

    def sell_limit(self, symbol: str, units: int, limit_price: float) -> int:
        """
        Coloca una orden LMT (limit) SELL de `units` acciones de `symbol`
        a un precio mínimo de `limit_price`. Nunca salta a mercado.
        Devuelve el orderId.
        """
        contract = self.createContract(symbol)
        int_units = math.floor(units)
        limit_price = round(limit_price, 2)  # Redondea a 2 decimales
        order = LimitOrder('SELL', int_units, limit_price)
        self.ib.placeOrder( contract, order)
        self.ib.sleep(1)  
        print(f"[SELL-LMT] {int_units} {symbol} @ {limit_price}")


    def createContract(self,symbol):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = 'STK'
        
        now= datetime.datetime.now(pytz.timezone('US/Eastern'))
        if now.hour<16:
            smart="SMART"
        else:
            smart="OVERNIGHT"
        
        contract.exchange = smart
        if symbol=="META":
            contract.primaryExchange = "NASDAQ"

        contract.currency = 'USD'
        return contract
    

if __name__ == "__main__":
    d=DriverIB(7497)
    d.conectar()
    #d.profolio()
    d.cash()
    d.clearOrders()
    #d.buy_limit("AAPL", 10, 150.00)
    #d.sell_limit("GOOG", 257, 169.55)

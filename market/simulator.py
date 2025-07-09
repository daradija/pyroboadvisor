
import numpy as np

class DDPP:
    def __init__(self,windowSize):
        self.d= np.zeros(windowSize, dtype=np.float64)
        self.i=0
        self.size=1
        self.total=0
        self.base=0

    def add(self, value):
        n=0
        for i in range(self.size):
            if value < self.d[i]:
                n+=1
        cur=n/self.size
        self.total += n
        self.base+=self.size
        self.d[self.i] = value
        self.i = (self.i + 1) % self.d.size
        if self.size < self.d.size:
            self.size += 1
        return 1-cur, 1-self.total/self.base

class Simulator:
    def __init__(self,symbols,comisionFija=0.0035+(0.000166+0.000022)-0.002):
        self.money = 0
        size=len(symbols)
        self.stocks=np.zeros(size, dtype=np.int16)
        self.pBuy=np.zeros(size)
        self.amount=np.zeros(size)
        self.pSell=np.zeros(size)
        self.numberOfStocksInPortfolio=0
        self.symbols=symbols
        self.initial=True
        self.comisionFija=comisionFija
        self.comision=0
        self.totalComision=0
        self.ddpp=DDPP(240)
        self.initialProgram=False

    def set_portfolio(self, money, stocks):
        self.money = money
        self.stocks = np.array(stocks, dtype=np.float64)
        
    def clone(self):
        new_simulator = Simulator(self.symbols, self.comisionFija)
        new_simulator.money = self.money
        new_simulator.stocks = np.copy(self.stocks)
        new_simulator.pBuy = np.copy(self.pBuy)
        new_simulator.amount = np.copy(self.amount)
        new_simulator.pSell = np.copy(self.pSell)
        new_simulator.numberOfStocksInPortfolio = self.numberOfStocksInPortfolio
        new_simulator.initial = self.initial
        new_simulator.comisionFija = self.comisionFija
        new_simulator.comision = self.comision
        new_simulator.totalComision = self.totalComision
        new_simulator.initialProgram = self.initialProgram
        new_simulator.ddpp = None
        return new_simulator

    def programBuy(self, id, price, amount):
        self.pBuy[id]= price
        self.amount[id] = amount
        self.initialProgram = True

    def programSell(self, id, price, amount):
        self.pSell[id] = price
        self.amount[id] = amount
        self.initialProgram = True

    def execute(self, low, high, close,date):
        if not self.initialProgram:
            return 
        if self.initial:
            self.initialMoney=self.money
            self.initialDate=date
            self.initial = False

        amounts=self.amount>0
        low2=low*amounts
        high2=high*amounts
        
        buy1=low2<self.pBuy 
        buy2=self.pBuy<high2
        buy=buy1 & buy2
        intBuy=np.array(self.amount/self.pBuy, dtype=np.int16)
        self.stocks+=np.where(self.pBuy==0,0,buy*intBuy)
        self.money-=np.sum(buy*intBuy*self.pBuy)

        self.comision= np.sum(buy*intBuy*self.comisionFija)

        # Pendiente de implementar la venta
        sell1=low2<self.pSell 
        sell2=self.pSell<high2
        sell=sell1 & sell2
        self.stocks=np.where(sell,0,self.stocks)
        self.money+=np.sum(sell*self.amount)

        self.comision+= np.sum(sell*self.amount*self.comisionFija)
        self.money -= self.comision
        # Imprime la comisión con dos decimales
        print(f"Comisión: ${self.comision:.2f}")
        self.totalComision += self.comision
        self.comision=0

        # Resetea las órdenes
        self.pBuy[:]=0
        self.pSell[:]=0
        self.amount[:]=0

        # Tasación
        tasacion=self.money+ np.sum(self.stocks*close)
        self.numberOfStocksInPortfolio = np.count_nonzero(self.stocks)
        print(str(date)[:11]+"Value: $"+str(int(tasacion)),end=" ")
        print("$"+str(int(self.money)), end=" ")
        for i in self.stockIndex():
            print(self.symbols[i]+"/"+str(self.stocks[i]), end=" ")

        if self.ddpp is None:
            return tasacion

        ddpp1,ddpp2= self.ddpp.add(tasacion)

        print()
        period= date - self.initialDate
        days=period.days + period.seconds/86400+1
        tae= (tasacion / self.initialMoney)**(365/days) - 1
        print("TAE: {:.2%}".format(tae), end=" ")
        print("DDPP: {:.2%}/{:.2%}".format(ddpp1, ddpp2), end=" ")
        self.tae= tae
        self.ddpp1=ddpp1
        self.ddpp2=ddpp2


        if tasacion<-self.money:
            print("Quebrado")
        return tasacion

    def stockIndex(self):
        return np.nonzero(self.stocks)[0]

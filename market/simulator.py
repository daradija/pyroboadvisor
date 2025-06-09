
import numpy as np

class Simulator:
    def __init__(self,source):
        self.money = 0
        self.stocks=np.zeros(source.size)
        self.pBuy=np.zeros(source.size)
        self.amount=np.zeros(source.size)
        self.pSell=np.zeros(source.size)

    def programBuy(self, id, price, amount):
        self.pBuy[id]= price
        self.amount[id] = amount

    def programSell(self, id, price, amount):
        self.pSell[id] = price
        self.amount[id] = amount

    def execute(self, low, high, close):
        amounts=self.amount>0
        low2=low*amounts
        high2=high*amounts
        sell=low<self.pSell<high
        buy=low<self.pBuy<high

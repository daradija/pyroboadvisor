import numpy as np
from pandas import Timestamp

class SourcePerDay:
    def __init__(self, source: str):
        self.source = source
        self.index=np.zeros(source.size,dtype=np.int16) # estos punterios apuntan al día de la fuente
        self.size=source.size
        self.symbols=source.symbols
        self.current=Timestamp(source.fecha_inicio) 
        self.repunteaIndex2()

    def nextDay(self):
        # Recolrre las velas y selecciona el mínimo día.
        min_day=None
        for i,c in enumerate(self.source.dates):
            if len(c) <= self.index[i] + 1:
                return False  # No hay más días disponibles
            current=c[self.index[i]+1]
            if min_day is None or (self.current<current and current < min_day):
                min_day = current
        self.current= min_day
        self.repunteaIndex()
        return True  # Se avanzó al siguiente día
    
    def repunteaIndex(self):
        for i,c in enumerate(self.source.dates):
            current=c[self.index[i]+1]
            if current== self.current:
                self.index[i] += 1
        self.repunteaIndex2()
        
    def repunteaIndex2(self):
        self.open=[self.source.open[i][j] for i,j in enumerate(self.index)]
        self.close=[self.source.close[i][j] for i,j in enumerate(self.index)]
        self.high=[self.source.high[i][j] for i,j in enumerate(self.index)]
        self.low=[self.source.low[i][j] for i,j in enumerate(self.index)]

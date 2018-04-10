import pandas as pd
import numpy as np

# COP from a daikin chart
#m=(4.5-2.2)/(15+10)
#b=4.5-m*15

MAXHEAT = 3.5 # kW

class HP:
    def __init__(self,size=MAXHEAT):
        self.maxheat = size

    def apply(self,data):
        df = self.df = data
        df['prload'] = df.rload
        self.hpload()
        df.rload = df.hpload
        
    def hpload(self):
        df = self.df
        # Calculate the residual post-HP load, hpload.
        df['hpout'] = np.minimum(df.rload,self.maxheat)
        df['hpload'] = df.rload - df.hpout
        df['COP'] = df.OAT * .092 + 3.12
        df['hpcons'] =  df.hpout / df.COP
        df.cons = df.cons + df.hpcons

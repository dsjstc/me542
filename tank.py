import pandas as pd
import numpy as np

# Tank went from 60 to 40 in 96 hours at 10 OAT--> k=.014
newtonK = -1/96*np.log((40-10)/(60-10))
def tankCool(ttank, oat): 
    return oat + (ttank - oat)*np.exp(-newtonK)

class Tank():
    def __init__(self):
        pass

    def apply(self,data):
        self.df = data
        self.iterTankAdd()

    def applyoat(self):
        df = self.df
        # Use newton's cooling model to determine the hourly tank 
        # temperature assuming no inputs or outputs except OAT.
        ttank=df.iloc[0].OAT
        for i,row in df[['OAT']].iterrows():
            ttank = tankCool(ttank,row.OAT)
            df.loc[i,'ttank'] = ttank
        
    def iterTankAdd(self):
        df = self.df
        
        # Set up for loop
        ttank=df.iloc[0].OAT
        df['addtank']=0
        
        # Now iteratively calculate the tank temperature by hour
        #mini = df[['OAT','exheat', 'ttank', 'rload']]
        mini = df[['OAT','exheat','rload']]
        for i,row in mini.iterrows():
            #tank temperature at end of hour due to heat loss T=OAT+(TTi-OAT)e^-k
            ttank = tankCool(ttank,row.OAT)
            
            # Capacity of 3800L tank: 4.42 kWh/degC
            # Increase in tank temperature from excess heat 
            addtank = max(0,row.exheat/4.42)
            df.loc[i,'addtank'] = addtank
            
            # Tank temp decrease from heat extraction
            if (row.rload > 0) & (ttank > 35.0):
                df.loc[i,'tankextract'] = row.rload * 100
                addtank = addtank - row.rload/4.42
                df.loc[i,'rload'] = 0
            
            ttank = ttank + addtank
            df.loc[i,'ttank'] = ttank
            #print("dt: %.4f tt: %.2f"%(dttank,ttank))    
            
            

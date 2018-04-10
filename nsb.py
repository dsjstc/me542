import numpy as np
WARMRATE=0.5

class NSB:

    def apply(self,data):
        self.df = data

    def iterrt(self):
        df = self.df
    
        # First we'll calculate the hourly RT for NSB: nrt
        df['nrt']=0.0
        rt=22
        newtonK=0.036
        for i,row in df.iterrows():
            rtsp = row.nrtsp
            delta = float(rtsp-rt)
            #print("D: %f"%delta)
            if delta > 0:
                # increase temperature by delta to a max of 1
                if delta > 1: delta = WARMRATE
            elif delta < 0:
                # newton's law of cooling for T=+1
                rt1 = row.OAT + (rt-row.OAT)*np.exp(-newtonK)
                CDRATE = rt1-rt
                #print("CD: %f"%CDRATE)
                if delta < CDRATE: delta = CDRATE
            rt = rt + delta
            df.nrt.at[i]= rt
            #print("%d rtsp=%f rt=%f delta=%f oat=%f" % (i.hour,rtsp,rt,delta,row.OAT))
            
    def calchds(self):
        df = self.df
        
        # Now calculate the sum of delta-T for BAU vs NSB (heating only)
        df['bauhd']=df.rt-df.OAT   # hourly bau delta T
        df['nsbhd']=df.nrt-df.OAT  # hourly nsb delta T
        
        # Eliminate negative delta T
        df.loc[df['bauhd']<0,'bauhd']=0 
        df.loc[df['nsbhd']<0,'nsbhd']=0
        
        #project savings
        self.heatDTsaved = (df.bauhd.sum() - df.nsbhd.sum()) 
        self.heatfracsaved = self.heatDTsaved/df.bauhd.sum()
        print("Heating savings: %.2f%%"%(100*heatfracsaved))
        #df.nsbhd.describe()
        #df.bauhd.describe()        

    def saveDT(row):
        RTN=row.nrt
        RTB=row.rt
        OAT=row.OAT
        # Computes the fractional reduction in delta T for NSB as compared to BAU
        DTN=RTN-OAT
        DTB=RTB-OAT
        if(DTB<=0): return 0 # There are no savings possible if the BAU DT indicates no heating.
        if(DTN<=0): DTN=0 # Best we can do is turn off the heat and save 100%
        return (DTB-DTN)/DTB

    def calcCoolAndSS(self):
        # Categorize periods and calculate new heating load for each period
        h = df[(df.hload!=0)].dropna()
        # Set default values for cooling
        h['cooldown']= h.nrt > h.nrtsp
        h.loc[h.cooldown,'savefrac'] = 1
        h.loc[h.cooldown,'nhload'] = 0 

        #compute savings fraction and hload for the Steady State periods
        # I think there's an error here.
        h['ss']= h.nrt == h.nrtsp
        #h['savefrac'] = 
        h.loc[h.ss,'savefrac']=h[h.ss].apply(saveDT,axis=1)
        h.loc[h.ss,'nhload']=h[h.ss]['hload'] * (1-h[h.ss]['savefrac'])

        #now get ready for the warmup rows
        h['warmup']= h.nrt < h.nrtsp
        self.h = h
        
    def calcWarmups(self):
        h = self.h
        
        # calculate the expected total NSB heating load, and the number of hours over which it should be distributed
        hw = pd.DataFrame(h[h.warmup])

        # Count the whole and fractional hours where warmup occurs
        hw['whrs'] = hw.nrtsp - hw.nrt # This is correct where DT<=1
        hw.loc[hw.whrs>1,'whrs'] = 1 # Because whrs is 1 where DT>1
        whrs = hw.whrs.sum()

        # Total Warmup heating is expected NSB total, less expected NSB at SS.
        expectedHnsb = h.hload.sum() * (1-heatfracsaved) 
        expectedHss = h[h.ss].hload.sum()
        expectHwarmup = expectedHnsb - expectedHss

        # Now distribute the warmup load
        HwarmPerWhr = expectHwarmup / whrs 
        h.loc[hw.index,'nhload'] = (hw.whrs * HwarmPerWhr)

        # There is an error here:
        h.nhload.sum() / h.hload.sum()

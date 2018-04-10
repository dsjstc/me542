# Calculate the collector efficiency
import numpy as np
#TUBEAREA = 3.13  # 3.13 per $1800 unit
DEFTUBEAREA = 3.13 # * 2
DEFANGLE=20.6 # Yes, this is the optimal value!

class HSolar:
    def __init__(self,tubearea=DEFTUBEAREA):
        self.tubearea = tubearea
    
    def apply(self, data):
        df = self.df = data

        df['prload'] = df.rload

        self.setVacEfficiency()
        self.collheat()
        self.savheat()
        self.applySLoad()
    
    def setVacEfficiency(self,watertemp=32.5):
        # Matrix-style operation.
        # Requires constant average water temperature.
        df = self.df
        df['dt'] = np.maximum(0,32.5 - df.OAT)
        df['soleff'] = np.maximum(0,(53.0 - 0.12 * df.dt)/100)

    # Use the efficiency and efficacy (angle) to calculate the actual useful heat collected
    def collheat(self,angle=DEFANGLE,sign=1):
        df = self.df
        # Angle is angle from VERTICAL!
        # IE, if the sun is at 20 degrees above horizon, and panel is at 20 degrees, 
        # then the sun is normal to the panel.
        
        # Calculate the angle of solar incidence (rads)
        df['solanginc']=np.abs(angle-df.sunalt[df.sunalt>0])*np.pi/180
        # Calculate fraction of panel normal to sun
        df['normalfraction']=np.cos(df['solanginc'])

        # How much heat is collected?
        # total available solar heat is (IrrDrN + IrrDfH) kWh/m^2
        df['solheat'] = self.tubearea * \
                        (df.IrrDfH * np.cos((90 - angle)*np.pi/180)
                         + df.normalfraction * df.soleff * df.IrrDrN )
        # 
        #print("Total collected heat (angle %.2f): %.2f kWh"%(FIXEDANGLE, df.solheat.sum()))

    def savheat(self,sign=1):
        # Having determined how much heat the panel has collected, apply it 
        # either against the residual load, or to the storage tank.
        # NB that the result goes to 'sload' (to allow repeated runs for opt)
        df = self.df
        
        # Savings if panel was always normal to sun.
        df['normsav'] = np.minimum(df.rload,(self.tubearea * (df.IrrDfH + df.soleff * df.IrrDrN).fillna(0))) 
        
        #Find the load after applying solar savings to pre-existing residual
        df['sload'] = np.maximum(0,df.rload - df.solheat.fillna(0))
        
        # Savings is the lesser of rload and solar heat. (ie, you can't save more than demand, and can't save more than there is to be saved.)
        df['sav'] = np.minimum(df.rload,df.solheat.fillna(0))
        
        #df[['hload','solheat','rload']]
        return (sign>0)*df.sav.sum()
        
    def applySLoad(self):        
        df = self.df
        # How much solar heat was unused?  Add it to "excess heat" exheat.
        df['exheat'] = df.exheat + np.maximum(0,df.solheat.fillna(0) - df.rload.fillna(0))
        # We're done calculating, so apply the sload to the standard rload column.
        df.rload = self.df.sload
        
    def collAndSave(self,angle,sign=1):
        self.collheat(angle)
        return self.savheat()
    
    def optAngle(self):
        # Apply numeric optimization to find the most effective angle for the collector
        # Only use this interactively.  It's not part of apply()
        import scipy.optimize as op
        return op.minimize(self.collAndSave,DEFANGLE,tol=.001)
        #return op.minimize(self.collAndSave,DEFANGLE,args=(-1),method='Nelder-Mead',tol=.00001)   
    
        

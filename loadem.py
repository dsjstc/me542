import pandas as pd
import numpy as np
from datetime import datetime

WXNAMES={'Date/Time':'Dtime', 'Time':'Hour','Data Quality':'Quality', 'Temp (°C)':'OAT', 
    'Dew Point Temp (°C)':'Dewpoint', 'Rel Hum (%)':'Relhum', 'Wind Dir (10s deg)':'Windir', 
    'Wind Spd (km/h)':'Winspd', 'Stn Press (kPa)':'Press', 'Hmdx':'Hmdx', 'Wind Chill':'Winchill'}
HYNAMES={'Interval Start Date/Time':'Dtime', 'Net Consumption (kWh)':'cons'}        

DEFHNAME = 'allhydro.csv'
#wname = 'allwx-entrance.csv'
DEFWNAME = 'allwx-ycd.csv'
DEFPICKLE = 'wxhydro2018.pickle'

def readPickle():
    return pd.read_pickle(DEFPICKLE)

def loadem(wname=DEFWNAME,hname=DEFHNAME):
    wx = loadwx(wname)['2015-06-04':]
    hy = loadhy(hname)

    data = hy.merge(wx.sort_index(),how='outer',left_index=True,right_index=True).sort_index()
    #data['doy']=data.index.dayofyear
    #data['moy']=data.index.month
    return data
    
def makePickles(df,pickle=DEFPICKLE):
    df.to_pickle(pickle)

def loadwx(wname=DEFWNAME):
    # Load the specified CSV
    wx = pd.read_csv(wname,header=0,parse_dates=['Date/Time'])
    
    
    wx.rename(columns=WXNAMES, inplace=True)
    wx.set_index(pd.DatetimeIndex(wx.Dtime),inplace=True)
    #wx['Hour'] = wx.index.hour
    wx = wx[~wx.index.duplicated(keep='first')]
    wx.drop(['Dtime','Year','Month','Day','Hour'],axis=1,inplace=True) # Indexed; no longer needed.
    return wx
    
def loadhy(hname=DEFHNAME):
    hy = pd.read_csv(hname
                     ,header=0
                     ,parse_dates=['Interval Start Date/Time']
                    )
    hy.rename(columns=HYNAMES, inplace=True)
    hy.set_index(pd.DatetimeIndex(hy.Dtime),inplace=True)
    hy = hy[~hy.index.duplicated(keep='first')]
    hy.drop('Dtime',axis=1,inplace=True) # Indexed; no longer needed.

    return hy

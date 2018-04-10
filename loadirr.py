import pandas as pd
COLWID = [ 7,1,10,4,4,2,4,2,4,2,4,1,4,1,4,1,4,1,2,1,4,1,4,1,4,1,8,1,5,1,4,1,4,1,3,1,4,1,2,1,2,1 ]
COLNMS = [ "ID", "Source", "Dtime", "IrrET", "IrrGlH", "IrrGlH-F", "IrrDrN", "IrrDrN-F", "IrrDfH", 
          "IrrDfH-F", "IrrGlHL", "IrrGlHL-F", "IrrDrNL", "IrrDrNL-F", "IrrDfHL", "IrrDfHL-F", 
          "IrrZ", "IrrZ-F", "SunMinutes", "SunMinutes-F", "Ceiling", "Ceiling-F", "SkyOctas", "SkyOctas-F", 
          "Vis100m", "Vis100m-F", "WxCode", "WxCode-F", "Pressure", "Pressure-F", "OAT", "Temp-F", 
          "Dewpoint", "Dewpoint-F", "WindDir", "WindDir-F", "Wind_kmh", "WindSpeed-F", 
          "SkycoverTotal", "SkycoverTotal-F", "SkycoverOpaque", "SkycoverOpaque-F", "SnowCover", 
          "SnowCover-F" ]
DEFINPUT = "CAN_BC_ENTRANCE-ISLAND_1022689_CWEEDS2011_T_N.WY3"

KEEPCOLS = [ 'IrrET',   'IrrGlH',  'IrrDrN',  'IrrDfH', 'Pressure', 'OAT', 'Dewpoint', 'WindDir', 'Wind_kmh','sunalt','sunaz' ]

# Irradiance Glossary
# Units are kJ/m2 during this hour (don't forget, we've subtracted 1 from the time during parsing!)
# ET/G/Dr/Df - extraterrestrial/Global/Direct/Diffuse
# H/N - Horizontal / Normal
# L suffix - illuminance in lux 

DEFPICKLE = 'irradiance2014.pickle'

def readPickle():
    return pd.read_pickle(DEFPICKLE)

def loadirr(fname=DEFINPUT):
    df = loadfwf(fname)
    df = cleanup(df)
    df = loadSunAltAzi(df)
    # df = calcSunAltAzi(df) # Use the loader above unless you have a very good reason.  This is slow!
    kp = makeKeep(df)
    #makePickles(df)
    return kp

def loadfwf(fname=DEFINPUT):
    df = pd.read_fwf(
          fname
        , widths=COLWID
        , header=None 
        , names=COLNMS
        #, index_col='Dtime'
        #, parse_dates=['Dtime']
        #, date_parser=dateparse
        , skiprows=1
        #, skiprows=50000
        #, nrows=50
        )
    return df

FMT='%Y%m%d%H'
def dateparse(x):
    # CWEEDS shows data in period ending at clock time 1-24 
    # but we need data during period starting at hour 
    # and strptime needs a 0-23 hour anyhow.
    idate = x - 1
    st = pd.datetime.strptime(idate, FMT)
    
def cleanup(df):
    # Date cleanup
    ######################################3
    d = (df.Dtime - 1).astype(str)
    df.index = pd.to_datetime(d, format=FMT)

    # Unit conversion
    ######################################3
    # Unit conversion
    df['OAT'] = df['OAT']/10              # To degC
    df['Wind_kmh'] = df['Wind_kmh']*0.36  # From units of .1m/s to km/h
    df['Dewpoint'] = df['Dewpoint']/10      # To degC
    df['Pressure'] = df['Pressure']/100     # from 10Pa to kPa

    # All irradiances to kWh
    df.IrrET = df.IrrET / 3600
    df.IrrGlH = df.IrrGlH / 3600
    df.IrrDrN = df.IrrDrN / 3600
    df.IrrDfH = df.IrrDfH / 3600

    return df

from pysolar.solar import *
import datetime
import warnings
warnings.filterwarnings('ignore') # pysolar v0.7 warns that it doesn't know leap seconds past 2015.

def loadSunAltAzi(df):
    df[['sunalt','sunaz']] = pd.read_pickle('sunangles.pickle')    
    return df

def calcSunAltAzi(df):
    # WARNING -- VERY SLOW!
    # You can probably just reload the sun data from the full_irradiance.pickle, below.
    # Currently disabled with <esc>-R
    # Enable with <esc>-Y

    # Nanaimo - Bowen Park
    lat = 49.174812
    lon = -123.960106

    def sunloop(s):
        #todo: This method would benefit from being parallelized.  Dask might be the way.  Look here:
        # http://dask.pydata.org/en/latest/dataframe.html
        for i,row in s.iterrows():
            date = i.to_pydatetime()#.tz_localize('America/Vancouver')
            al = s.loc[i,'sunalt']  = get_altitude(lat, lon, date)
            az = s.loc[i,'sunaz'] =  get_azimuth(lat,lon,date)
            
            # Correct for major bug in azimuth calculation
            if az>=-180: az =  180 - az
            else:        az = -180 - az

    sunloop(df)    
    
    # If you're absolutely sure that you've recreated the sun location data correctly
    # Use this to repickle it.  Use with care, calculating takes an hour.
    #df[['sunalt','sunaz']].to_pickle('sunangles.pickle')

def makeKeep(df):
    # Create a pickle with the stuff we are likely to want in the models
    kp = pd.DataFrame(df[KEEPCOLS])['2012':'2014']
    return kp
    
def makePickles(df):
    kp = makeKeep(df)
    kp.to_pickle(DEFPICKLE)
    
    # Create these ones just in case
    kpbig = pd.DataFrame(df[KEEPCOLS])    
    kpbig.to_pickle('big_irradiance1998-2014.pickle')
    
    # Create a big pickle with every bit of the data
    df.to_pickle('wide_big_irradiance1998-2014.pickle')

    # NB that the "sunangles.pickle" was also created up there somewhere.

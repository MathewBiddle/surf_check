# python3.7
import numpy as np
#import pygrib
import matplotlib.pyplot as plt
#from mpl_toolkits.basemap import Basemap
import sys
import datetime, pytz
import pandas as pd

## This script will import the NDBC wave information file and plot the data
# This assumes the conventions follow https://www.ndbc.noaa.gov/waveobs.shtml
#
# Future development:
#  1. look at SwH gradient. if > x send a notification (run every hour)
#  2. combine this with model data reading. overlay model w/ obs for forecast

##---------user defined options---------------#
duration=4 # days
buoy_id=44097 # block island 40.969 N 71.127 W
##
## No need to edit below here
## the rest of the script will run on its own
## -------------------------------------------#

# collect time information
startday=datetime.datetime.utcnow()-datetime.timedelta(days=duration)
startday=startday.replace(tzinfo=pytz.timezone('UTC')) # assign utc timezone
now = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone('UTC')) # in UTC
#print(startday.strftime("%Y-%m-%d %H:%M:%S %Z%z"))
print(\
    "Script ran on: %s US/Eastern"%\
     now.astimezone(\
        pytz.timezone('US/Eastern')\
                    ).strftime("%Y-%m-%d %H:%M:%S")\
     )


# grab buoy data
url="https://www.ndbc.noaa.gov/data/realtime2/%s.spec"%buoy_id
dict_dtype={'#YY' : np.int32,\
            'MM' : np.int32,\
            'DD' : np.int32,\
            'hh' : np.int32,\
            'mm' : np.int32,\
            'WVHT' : np.float64,\
            'SwH' : np.float64,\
            'SwP' : np.float64,\
            'WWH' : np.float64,\
            'WWP' : np.float64,\
            'SwD' : str,\
            'WWD' : str,\
            'STEEPNESS' : str,\
            'APD' : np.float64,\
            'MWD' : np.float64}
df=pd.read_fwf(url,header=[0],skiprows=[1],parse_dates={'date':[0,1,2,3,4]},keep_date_col=True,dtype=dict_dtype)

# do some reformatting of the data
df['date_utc']=pd.to_datetime(df['date'],format="%Y %m %d %H %M",utc=True) # create datetime object
df.index=df.date_utc # set date to header
#del df.index.name # remove the index name
df.drop(['date_utc','date','#YY','MM','DD','hh','mm'],1,inplace=True) # remove unnecessary cols
df.sort_index(inplace=True)
#df['SwH']=df['SwH']*3.28084 # convert to feet

## convert timezones before subsetting
#df.set_index(df.index.tz_convert('US/Eastern'),append=True,inplace=True)
#df.index.rename(['date_utc','date_EST'],inplace=True)
#print(df.index.name)
#sys.exit()

# subset the data
dfsubset=df['SwH'].loc[startday.strftime("%Y%m%d"):now.strftime("%Y%m%d")]
#dfsubset.index=dfsubset.index.tz_convert('US/Eastern') # convert to EST
# plot
dfsubset.plot(subplots=True)
titletxt='NDBC buoy %s Wave Information'%buoy_id
#plt.ylim(0,15)
plt.title(titletxt)
plt.ylabel('SwH (ft)')
plt.xlabel(dfsubset.index.tz)
plt.show()


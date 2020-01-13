def process_grib(ptlat,ptlon):
   # python3.7
   import numpy as np
   import pygrib
   import matplotlib.pyplot as plt
   #from mpl_toolkits.basemap import Basemap
   #import sys
   import datetime
   #import pytz
   import os
   import pandas as pd
   ## file downloaded from:
   #https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwps/prod/er.20190206/box/06/CG1/
   
   ## to download the file
#   now = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone('UTC')) # in UTC
   now = datetime.datetime.now()
   #today = datetime.datetime.today().strftime("%Y%m%d")
   filename="box_nwps_CG1_%s_1200.grib2"%now.strftime("%Y%m%d")
   
   if not os.path.isfile('data/'+filename):
      print("%s does not exist in current directory.\nDownloading now from:"%filename)
      urlbase="https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwps/prod/er.%s/box/12/CG1/"%now.strftime("%Y%m%d")
      url=urlbase+filename
      print(url)
      import wget
      wget.download(url,out='data/'+filename)
      print("\nDownload complete.")
   else:
      print("data/%s exists, continuing..."%filename)
   
   #filename='box_nwps_CG1_20190207_0600.grib2';
   grbs=pygrib.open('data/'+filename)
   
   ## Determine coordinates for the location I want, exract data, make timeSeries plot.
   ## Block Island Buoy 40.969 N 71.127 W
   ##
   
   grb = grbs.select(name='Significant height of swell waves')[0]
   lat,lon = grb.latlons()
   data=grb.values
   time=grb.validDate
   
   ## find a point
   lat_X=np.abs(lat - ptlat)
   lat_idx=np.where(lat_X==lat_X.min())[0][0]
   lon_X=np.abs(lon - (360-ptlon))#288.873)
   lon_idx=np.where(lon_X==lon_X.min())
   
   ## Make a map
   if 1==1:
       plt.figure()
       plt.pcolor(lon,lat,data)
#      m=Basemap(projection='mill',lat_ts=10,llcrnrlon=lon.min(), \
#        urcrnrlon=lon.max(),llcrnrlat=lat.min(),urcrnrlat=lat.max(), \
#        resolution='f')
   
#      x, y = m(lon,lat)
#      cs = m.pcolormesh(x,y,data,shading='flat',cmap=plt.cm.jet)
#      lx,ly=m(lon[lon_idx][lat_idx],lat[lon_idx][lat_idx])
#      m.plot(lx,ly,'ko',markersize=5)
#      m.drawcoastlines()
#      m.fillcontinents()
#      m.drawmapboundary()
#      m.drawparallels(np.arange(-90.,120.,1.),labels=[1,0,0,0])
#      m.drawmeridians(np.arange(-180.,180.,1.),labels=[0,0,0,1])
       plt.plot(lon[lon_idx][lat_idx], lat[lon_idx][lat_idx], 'ko', markersize=5)
       cb = plt.colorbar(orientation='vertical')
       cb.ax.set_ylabel('Significant Height [m] of Swell Waves from NWPS')
       plt.title('%s'%time)
 #     plt.show()
   
   ## grab point data
   ptdata=[]
   date=[]
   for grb in grbs:
      if grb.parameterName=='Significant height of swell waves':
         ptdata.append(grb.values[lon_idx][lat_idx])
         date.append(datetime.datetime.fromisoformat(str(grb.validDate)))
   
   df=pd.DataFrame({"NWPS" : ptdata,
                          "date_utc":date})
   df.date_utc=pd.to_datetime(df.date_utc,utc=True)
   df.set_index('date_utc',inplace=True)
   #df.plot()
   #plt.show()
   return df;

def process_ndbc(buoy_id,duration):   
   # python3.7
   import numpy as np
   #import pygrib
   #import matplotlib.pyplot as plt
   #from mpl_toolkits.basemap import Basemap
   #import sys
   import datetime, pytz
   import pandas as pd
   
   ## This script will import the NDBC wave information file and plot the data
   # This assumes the conventions follow https://www.ndbc.noaa.gov/waveobs.shtml
   #
   # Future development:
   #  1. look at SwH gradient. if > x send a notification (run every hour)
   #  2. combine this with model data reading. overlay model w/ obs for forecast
   
   ##---------user defined options---------------#
   #duration=4 # days
   #buoy_id=44097 # block island 40.969 N 71.127 W
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
   dfsubset=pd.DataFrame(df['SwH'].loc[startday.strftime("%Y%m%d"):now.strftime("%Y%m%d")])
   dfsubset.columns=['NDBC'] # rename 'SwH' to 'NDBC'
   #dfsubset.index=dfsubset.index.tz_convert('US/Eastern') # convert to EST
   # plot
   #dfsubset.plot(subplots=True)
   #titletxt='NDBC buoy %s Wave Information'%buoy_id
   #plt.ylim(0,15)
   #plt.title(titletxt)
   #plt.ylabel('SwH (ft)')
   #plt.xlabel(dfsubset.index.tz)
   #plt.show()
   return dfsubset;
import matplotlib
matplotlib.use('MacOSX')
import matplotlib.pyplot as plt
import pandas as pd
import sys
#import pytz

buoy_id=44097 # block island 40.969 N 71.127 W
duration=4 # days
ptlat=40.969
ptlon=71.127
nwps=process_grib(ptlat,ptlon)
ndbc=process_ndbc(buoy_id,duration)
#data=pd.concat([dfsubset,df],axis=0,sort=True)
data=pd.merge(ndbc,nwps,how='outer',left_index=True,right_index=True)
data=data*3.281 # meters to ft

data.index = data.index.tz_convert('America/New_York')
data.rename_axis('date_est',inplace=True)
#data.sort_index(inplace=True)
#print(data.loc["20190209":"20190211"])
#data.to_csv('test.csv')
data.plot()
#plt.show()
#sys.exit()
#plt.figure()
#plt.plot(data.index,data.NDBC,'k.-',label='NDBC')
#plt.plot(data.index,data.NWPS,'r.',label='NWPS')
#data.plot()
#plt.title('Block Island 40.969N 71.127W')
plt.ylabel('Swell Height (ft)')
#plt.ylim(0,1.5)
#plt.legend()
plt.show()
#print(df.describe())
#print(dfsubset.describe())

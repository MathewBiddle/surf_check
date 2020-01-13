# python3.7
import numpy as np
import pygrib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import sys
import datetime
import pytz
import os
import pandas as pd
## file downloaded from:
#https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwps/prod/er.20190206/box/06/CG1/

## to download the file
now = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone('UTC')) # in UTC
#today = datetime.datetime.today().strftime("%Y%m%d")
filename="box_nwps_CG1_%s_0600.grib2"%now.strftime("%Y%m%d")

if not os.path.isfile(filename):
   print("%s does not exist in current directory.\nDownloading now from:"%filename)
   urlbase="https://nomads.ncep.noaa.gov/pub/data/nccf/com/nwps/prod/er.%s/box/06/CG1/"%now.strftime("%Y%m%d")
   url=urlbase+filename
   print(url)
   import wget
   wget.download(url)
   print("\nDownload complete.")
else:
   print("%s exists, continuing..."%filename)

filename='box_nwps_CG1_20190207_0600.grib2';
grbs=pygrib.open(filename)

## Determine coordinates for the location I want, exract data, make timeSeries plot.
## Block Island Buoy 40.969 N 71.127 W
##

grb = grbs.select(name='Significant height of swell waves')[0]
lat,lon = grb.latlons()
data=grb.values
time=grb.validDate

## find a point
lat_X=np.abs(lat - 40.969)
lat_idx=np.where(lat_X==lat_X.min())[0][0]
lon_X=np.abs(lon - (360-71.127))#288.873)
lon_idx=np.where(lon_X==lon_X.min())

## Make a map
if 2==1:
   m=Basemap(projection='mill',lat_ts=10,llcrnrlon=lon.min(), \
     urcrnrlon=lon.max(),llcrnrlat=lat.min(),urcrnrlat=lat.max(), \
     resolution='f')

   x, y = m(lon,lat)
   cs = m.pcolormesh(x,y,data,shading='flat',cmap=plt.cm.jet)
   lx,ly=m(lon[lon_idx][lat_idx],lat[lon_idx][lat_idx])
   m.plot(lx,ly,'ko',markersize=5)
   m.drawcoastlines()
   m.fillcontinents()
   m.drawmapboundary()
   m.drawparallels(np.arange(-90.,120.,1.),labels=[1,0,0,0])
   m.drawmeridians(np.arange(-180.,180.,1.),labels=[0,0,0,1])

   plt.colorbar(cs,orientation='vertical')
   plt.title('Significant Height of Swell Waves from NWPS on %s'%time)
   plt.show()

## grab point data
ptdata=[]
date=[]
for grb in grbs:
   if grb.parameterName=='Significant height of swell waves':
      ptdata.append(grb.values[lon_idx][lat_idx])
      date.append(datetime.datetime.fromisoformat(str(grb.validDate)))

df=pd.DataFrame({"swellH" : ptdata,
                       "date_utc":date})
df.date_utc=pd.to_datetime(df.date_utc,utc=True)
df.set_index('date_utc',inplace=True)
df.plot()
plt.show()


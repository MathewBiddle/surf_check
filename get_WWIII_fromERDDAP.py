
import datetime
import pandas as pd
import numpy as np

now = datetime.datetime.utcnow()-datetime.timedelta(days=1)
now = now.strftime('%Y-%m-%d')
#url = 'http://oos.soest.hawaii.edu/erddap/griddap/NWW3_Global_Best.csv?shgt%%5B(%s):1:(last)%%5D%%5B(0.0):1:(0.0)%%5D%%5B(36.0):1:(48.0)%%5D%%5B(270.0):1:(314.0)%%5D' % now
url = 'https://coastwatch.pfeg.noaa.gov/erddap/griddap/NWW3_Global_Best.csvp?shgt[(%s):1:(last)][(0.0):1:(0.0)][(41.0):1:(41.0)][(289.0):1:(289.0)]' % now
ww3 = pd.read_csv(url,index_col='time (UTC)',parse_dates=True,infer_datetime_format=True)

#sys.exit()
#ww3.drop(index='UTC',inplace=True)

#lat = 40.969
#lon = 360-71.127

#result = ww3.loc[(ww3['latitude'] == round(lat)) & (ww3['longitude'] == round(lon)), ['time','latitude','longitude','shgt']]

ww3['shgt (meters)'].plot()
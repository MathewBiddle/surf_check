
import datetime
import pandas as pd

now = datetime.datetime.utcnow().strftime('%Y-%m-%d')
url = 'http://oos.soest.hawaii.edu/erddap/griddap/NWW3_Global_Best.csv?shgt%%5B(%s):1:(last)%%5D%%5B(0.0):1:(0.0)%%5D%%5B(36.0):1:(48.0)%%5D%%5B(270.0):1:(314.0)%%5D' % now

ww3 = pd.read_csv(url,index_col='time',parse_dates=True,infer_datetime_format=True)
ww3.drop(index='UTC',inplace=True)

lat = 40.969
lon = 360-71.127

result = ww3.loc[(ww3['latitude'] == round(lat)) & (ww3['longitude'] == round(lon)), ['time','latitude','longitude','shgt']]

result['shgt'].plot()
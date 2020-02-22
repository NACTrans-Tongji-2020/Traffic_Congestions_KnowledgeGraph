# -*- coding:utf-8-*-
import pandas as pd
import geopandas as gp
import numpy as np
from shapely.geometry.point import Point
import time

print '1'
# header=None:没有每列的column name，可以自己设定
# encoding='gb2312':其他编码中文显示错误
# sep=',':用逗号来分隔每行的数据
# index_col=0:设置第1列数据作为index
st = time.time()
txt = pd.read_csv(r"C:\Users\Zero Yi\Documents\L\test\source\20161219_085.TXT",
                  header=None, encoding='gb2312', sep=',', index_col=None,
                  names=['Date', 'Time', 'Letter', 'Plate', 'Longitude', 'Latitude', 'Speed', 'Orientation',
                         'Load', 'Available'],
                  dtype={'Date': np.uint32, 'Time': np.uint32, 'Letter': str, 'Plate': str, 'Longitude': np.float32,
                         'Latitude': np.float32, 'Speed': np.uint8, 'Orientation': np.uint16, 'Load': bool, 'Available': bool})  # DataFrame对象
print '2'
txt.drop(['Letter', 'Load', 'Available'], inplace=True, axis=1)  # 去除无效数据

txt['geometry'] = txt.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
# for i in range(len(txt)):
#     txt.loc[i, 'geometry'] = Point(txt.loc[i,'Longitude'],txt.loc[i,'Latitude'])
#     print ('now at',i)

print '3'
data_geod = gp.GeoDataFrame(txt)  # 转换成GeoDF对象
# data_geod = data_geod.set_geometry('geometry')
data_geod.crs = {'init': 'epsg:4326'}
print '4'
data_geod.to_file(r'C:\Users\Zero Yi\Documents\L\test\GPS20161219_085.shp', encoding='gb2312')

print time.time()-st

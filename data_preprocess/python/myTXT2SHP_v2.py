# -*- coding:utf-8-*-
import pandas as pd
import geopandas as gp
import numpy as np
from shapely.geometry.point import Point
import time
import arcpy

###################
# 想法是这样，考虑到在analysis的时候，数据导入和intersection花的时间几乎同样多，
# 以及TXT2SHP的时候，也是样本越多时间越长。
#
# 现在想根据buffer的上下左右边界，划定矩形，留在里面的才导出成SHP
# 这样进入analysis的时候，导入数据和Intersection都会更快。
#
#
##########
st = time.time()
print '0'
# 首先读入buffer的上下左右边界经纬度，运行的时候buffer.shp文件不能被ARCGIS占用
# 此处有个很奇怪的bug，用Console的时候，凡是第一次运行的时候，会报错buufer.shp文件不能打开，但是第二次运行就可以了。
# 如果是直接运行.py，重复也不行。可能与arcpy也重载了有关。
# 所以使用try-except结构，强行跑两次。
inshp = r'C:\Users\Zero Yi\Documents\L\buffer_output\buffer.shp'
try:
    with arcpy.da.SearchCursor(inshp, 'SHAPE@') as cursor:
        for row in cursor:
            resultcode = row[0].extent
except:
    print 'here'
    with arcpy.da.SearchCursor(inshp, 'SHAPE@') as cursor:
        for row in cursor:
            resultcode = row[0].extent

XMax = resultcode.XMax # 经度
XMin = resultcode.XMin
YMax = resultcode.YMax # 维度
YMin = resultcode.YMin

print '1'
# header=None:没有每列的column name，可以自己设定
# encoding='gb2312':其他编码中文显示错误
# sep=',':用逗号来分隔每行的数据
# index_col=0:设置第1列数据作为index

txt = pd.read_csv(r"C:\Users\Zero Yi\Documents\L\test\source\20161219_085.TXT",
                  header=None, encoding='gb2312', sep=',', index_col=None,
                  names=['Date', 'Time', 'Letter', 'Plate', 'Longitude', 'Latitude', 'Speed', 'Orientation',
                         'Load', 'Available'],
                  dtype={'Date': np.uint32, 'Time': np.uint32, 'Letter': str, 'Plate': str, 'Longitude': np.float32,
                         'Latitude': np.float32, 'Speed': np.uint8, 'Orientation': np.uint16, 'Load': bool, 'Available': bool})  # DataFrame对象
print '2'
txt.drop(['Letter', 'Load', 'Available'], inplace=True, axis=1)  # 去除无效数据

txt = txt[ (txt['Longitude'] - XMax) < 0 ] # 右边剔除
txt = txt[ (txt['Longitude'] - XMin) > 0 ] # 左边剔除
txt = txt[ (txt['Latitude'] - YMax) < 0 ] # 上边剔除
txt = txt[ (txt['Latitude'] - YMin) > 0 ] # 下边剔除

# 将地理几何信息塞进去，不然无法转化成shp
txt['geometry'] = txt.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
# for i in range(len(txt)):
#     txt.loc[i, 'geometry'] = Point(txt.loc[i,'Longitude'],txt.loc[i,'Latitude'])
#     print ('now at',i)

print '3'
data_geod = gp.GeoDataFrame(txt)  # 转换成GeoDF对象
# data_geod = data_geod.set_geometry('geometry')
data_geod.crs = {'init': 'epsg:4326'} # 添加参考系
print '4'
data_geod.to_file(r'C:\Users\Zero Yi\Documents\L\test\GPS20161219_085_v2.shp', encoding='gb2312')

print time.time()-st

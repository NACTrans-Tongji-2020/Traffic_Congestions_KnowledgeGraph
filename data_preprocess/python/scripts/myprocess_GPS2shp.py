# -*- coding:gb2312 -*-
import pandas as pd
import geopandas as gp
import numpy as np
from shapely.geometry.point import Point
import arcpy, os
import gc

def preprocess (inshp):
    try:
        with arcpy.da.SearchCursor(inshp, 'SHAPE@') as cursor:
            for row in cursor:
                resultcode = row[0].extent
    except:
        print 'here'
        with arcpy.da.SearchCursor(inshp, 'SHAPE@') as cursor:
            for row in cursor:
                resultcode = row[0].extent

    XMax = resultcode.XMax  # 经度
    XMin = resultcode.XMin
    YMax = resultcode.YMax  # 维度
    YMin = resultcode.YMin

    return XMax, XMin, YMax, YMin

def GPS_2shp (txt_path, shp_path, XMax, XMin, YMax, YMin):

    files = os.listdir(txt_path)
    for txtfile in files:
        filetemp = txt_path + txtfile
        if not os.path.getsize(filetemp):
            os.remove(filetemp)
            print('Del Projection:', txtfile)
        else:
            txt = pd.read_csv(filetemp,
                              header=None, encoding='gb2312', sep=',', index_col=None,
                              names=['Date', 'Time', 'Letter', 'Plate', 'Longitude', 'Latitude', 'Speed', 'Orientation',
                                     'Load', 'Available'],
                              dtype={'Date': np.uint32, 'Time': np.uint32, 'Letter': str, 'Plate': str,
                                     'Longitude': np.float32,
                                     'Latitude': np.float32, 'Speed': np.uint8, 'Orientation': np.uint16, 'Load': bool,
                                     'Available': bool})  # DataFrame对象

            txt.drop(['Letter', 'Load', 'Available'], inplace=True, axis=1)  # 去除无效数据

            txt = txt[(txt['Longitude'] - XMax) < 0]  # 右边剔除
            txt = txt[(txt['Longitude'] - XMin) > 0]  # 左边剔除
            txt = txt[(txt['Latitude'] - YMax) < 0]  # 上边剔除
            txt = txt[(txt['Latitude'] - YMin) > 0]  # 下边剔除

            if not len(txt):
                print('Skip Projection:', txtfile)
                continue

            # 将地理几何信息塞进去，不然无法转化成shp
            txt['geometry'] = txt.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)

            data_geod = gp.GeoDataFrame(txt)  # 转换成GeoDF对象

            data_geod.crs = {'init': 'epsg:4326'}  # 添加参考系

            data_geod.to_file(shp_path + txtfile.split('.')[0] + '.shp', encoding='gb2312')

            print('Finish Projection:', txtfile)
            del txt
            del data_geod
            gc.collect()

if __name__ == '__main__':
    print 'begin'

    inshp = 'C:/Users/Zero Yi/Documents/L/data_preprocess/buffer_output/buffer.shp'
    XMax, XMin, YMax, YMin = preprocess(inshp)

    txt_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/test/source/'
    shp_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/test/shp/'
    GPS_2shp(txt_path, shp_path, XMax, XMin, YMax, YMin)

    print 'over'
    # for i in range(6):
    #     p = Process(target=GPS_2shp, args=(21,i,))
    #     p.start()
    #     p.join()

# -*- coding:utf-8 -*-
import pandas as pd
import os
import geopandas as gp
from shapely.geometry.point import Point


def anglesel(shpPath, anglexls, outputPath):
    '''
    对每个shp，里面匹配好了的每一个浮动点，找到其匹配的路段代码NEAR_FID，然后对比路段角度，
    如果不是锐角，则剔除这个浮动点。

    根据观察，xls是从dbf转得，而dbf是直接脱胎于shp，所以干脆直接操作对应的shp好了。
    顺便把SHP的过滤也在这里做了，即把operateSHP.py的工作在这里做了。

    :param selectpath:  需要校验的shp所在文件夹
    :param anglexls:  校验的路段角度xls文件
    :param outputPath: 符合预期的shp文件输出的文件夹
    :return:
    '''

    bh_angle_xls = pd.read_csv(filepath_or_buffer=anglexls, names=['FID', 'angle'], usecols=[0, 5], index_col="FID")

    files = os.listdir(shpPath)
    mapper = {'NEAR_X': "Longitude", 'NEAR_Y': 'Latitude'}  # 这个没必要在循环里重复定义

    for shpfile in files:
        if os.path.splitext(shpfile)[1] == '.shp':  # 过滤其他后缀文件
            filetemp = shpPath + shpfile
            geodf = gp.GeoDataFrame.from_file(filetemp)
            geodf = geodf[['Date', 'Time', 'Plate', 'Speed', 'Orientatio', 'NEAR_FID', 'NEAR_X', 'NEAR_Y', 'geometry']]
            geodf = geodf.rename(mapper=mapper, axis=1)  # 更改信息，认为校准之后的位置就是车辆的真实位置
            geodf['geometry'] = geodf.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1)
            # 需要把geometry之中的信息也对应替换

            for index, row in geodf.iterrows():
                Fid = row['NEAR_FID'] + 1  # 得到每个浮动点匹配到的路段,加一之后就是路段角度xls里面的索引
                angle_car = row['Orientatio']
                angle_road = bh_angle_xls.loc[Fid].values
                if abs(angle_car - angle_road) >= 90:  # 如果两个方向所夹不是锐角，则剔除这个点
                    geodf.drop(index=index, inplace=True, errors='ignore')
                    # print('point deleted:', index)

            geodf.to_file(outputPath + shpfile, encoding='gb2312')  # 输出shp
            print('Finish angleselect Projection:' + shpfile)

if __name__ == '__main__':
    shp_path = r'C:\Users\Zero Yi\Documents\L\data_preprocess\Intersect_analysis\bh_151\\'
    output_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/test/shpoperating/product/'
    anglexls = 'C:\\Users\\Zero Yi\\Documents\\L\\data_preprocess\\bh_divided\\151_degree.csv'

    anglesel(shp_path, anglexls, output_path)
    # print('使得')
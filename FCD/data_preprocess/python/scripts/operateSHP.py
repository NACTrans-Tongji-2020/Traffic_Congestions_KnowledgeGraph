# -*- coding:gb2312 -*-
import geopandas as gp
from shapely.geometry.point import Point
import os

def operateSHP(shpPath, outputPath):
    '''
    直接操作shp文件，进行一些删改操作
     A GeoDataFrame object is a pandas.DataFrame that has a column
    with geometry.
    记住这句话

    :param shpPath: 输入的shp文件所在文件夹
            outputPath: 符合预期的shp文件输出的文件夹
    :return: 无
    '''
    files = os.listdir(shpPath)
    mapper = {'NEAR_X': "Longitude", 'NEAR_Y': 'Latitude'} # 这个没必要在循环里重复定义

    for shpfile in files:
        if os.path.splitext(shpfile)[1] == '.shp':  # 过滤其他后缀文件
            filetemp = shpPath + shpfile
            geodf = gp.GeoDataFrame.from_file(filetemp)
            geodf = geodf[['Date', 'Time', 'Plate', 'Speed', 'Orientatio', 'NEAR_FID', 'NEAR_X', 'NEAR_Y', 'geometry']]
            geodf = geodf.rename(mapper=mapper, axis=1) # 更改信息，认为校准之后的位置就是车辆的真实位置
            geodf['geometry'] = geodf.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1) # 需要把geometry之中的信息也对应替换
            geodf.to_file(outputPath+shpfile, encoding='gb2312')

if __name__ == '__main__':
    shp_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/test/shpoperating/source/'
    output_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/test/shpoperating/product/'

    operateSHP(shp_path, output_path)
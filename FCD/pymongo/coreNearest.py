# 这个脚本文件用来对重心坐标进行最近邻分析的，需要调用Arcpy，而这个项目的解释器是python3
# 所以同样也只是放在这里，作为工程的一部分
# 实际运行请用含有arcpy的python2来跑

import arcpy
import pandas as pd
import geopandas as gp
from shapely.geometry.point import Point
import os


# 将csv变成shp
def csv2shp(path, shp_path):
    files = os.listdir(path)
    for csvfile in files:
        filetemp = path + csvfile
        df = pd.read_csv(filetemp, index_col=0)
        df['geometry'] = df.apply(lambda row: Point(row['CoreLongitude'], row['CoreLatitude']), axis=1)
        data_geod = gp.GeoDataFrame(df)  # 转换成GeoDF对象
        data_geod.crs = {'init': 'epsg:4326'}  # 添加参考系
        data_geod.to_file(shp_path + csvfile.split('.')[0] + '.shp', encoding='gb2312')

# 近邻分析
def nearAnalysis(shp_path, dissolved_file):
    for shpfile in os.listdir(shp_path):
        if os.path.splitext(shpfile)[1] == '.shp':  # 过滤其他后缀文件
            inputfile = shp_path + shpfile
            arcpy.Near_analysis(inputfile, dissolved_file, '#', 'LOCATION', 'ANGLE', 'PLANAR')

# 分析结果再变回excel
def DBF2EXCEL(input_path, output_path):
    '''
    :param input_path: 待转换的dbf文件所在文件夹
    :param output_path: 生产的csv文件存放的文件夹
    :return:
    '''
    for dbffile in os.listdir(input_path):
        if os.path.splitext(dbffile)[1] == '.dbf': # 过滤其他后缀文件
            inputfile = input_path + dbffile
            outputfile = output_path + os.path.splitext(dbffile)[0] + '.xls'
            print(outputfile)
            arcpy.TableToExcel_conversion(inputfile, outputfile)

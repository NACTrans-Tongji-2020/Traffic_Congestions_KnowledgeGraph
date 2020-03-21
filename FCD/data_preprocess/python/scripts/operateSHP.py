# -*- coding:gb2312 -*-
import geopandas as gp
from shapely.geometry.point import Point
import os

def operateSHP(shpPath, outputPath):
    '''
    ֱ�Ӳ���shp�ļ�������һЩɾ�Ĳ���
     A GeoDataFrame object is a pandas.DataFrame that has a column
    with geometry.
    ��ס��仰

    :param shpPath: �����shp�ļ������ļ���
            outputPath: ����Ԥ�ڵ�shp�ļ�������ļ���
    :return: ��
    '''
    files = os.listdir(shpPath)
    mapper = {'NEAR_X': "Longitude", 'NEAR_Y': 'Latitude'} # ���û��Ҫ��ѭ�����ظ�����

    for shpfile in files:
        if os.path.splitext(shpfile)[1] == '.shp':  # ����������׺�ļ�
            filetemp = shpPath + shpfile
            geodf = gp.GeoDataFrame.from_file(filetemp)
            geodf = geodf[['Date', 'Time', 'Plate', 'Speed', 'Orientatio', 'NEAR_FID', 'NEAR_X', 'NEAR_Y', 'geometry']]
            geodf = geodf.rename(mapper=mapper, axis=1) # ������Ϣ����ΪУ׼֮���λ�þ��ǳ�������ʵλ��
            geodf['geometry'] = geodf.apply(lambda row: Point(row['Longitude'], row['Latitude']), axis=1) # ��Ҫ��geometry֮�е���ϢҲ��Ӧ�滻
            geodf.to_file(outputPath+shpfile, encoding='gb2312')

if __name__ == '__main__':
    shp_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/test/shpoperating/source/'
    output_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/test/shpoperating/product/'

    operateSHP(shp_path, output_path)
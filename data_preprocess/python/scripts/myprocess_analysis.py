# -*- coding:gb2312 -*-
import arcpy
import os

def GPS_road_analysis(buffer_file, dissolved_file, shp_path, output_path):
    for shpfile in os.listdir(shp_path):
        if os.path.splitext(shpfile)[1] == '.shp': # 过滤其他后缀文件
            # print('processing ' + shpfile)
            inputfile = shp_path + shpfile
            outputfile = output_path + shpfile
            inFeatures = [inputfile, buffer_file]

            # Interscetion
            arcpy.Intersect_analysis(inFeatures, outputfile, 'ALL', '#', 'INPUT')

            # Near_analysis
            # arcpy.Near_analysis(outputfile, dissolved_file, '#', 'LOCATION', 'ANGLE', 'PLANAR')
            arcpy.Near_analysis(outputfile, dissolved_file, '#', 'LOCATION', 'NO_ANGLE', 'PLANAR')  # 感觉这个移动的角度没啥用
            print('Finish Analysis Projection:' + shpfile)
            del inFeatures

if __name__ == '__main__':
    print 'begin'

    buffer_file = 'C:/Users/Zero Yi/Documents/L/data_preprocess/buffer_output/buffer_151.shp'
    road_file = 'C:/Users/Zero Yi/Documents/L/data_preprocess/bh_divided/bh_divided_151.shp'

    shp_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/test/shp/'
    output_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/Intersect_analysis/bh_151/'

    GPS_road_analysis(buffer_file, road_file, shp_path, output_path)
    print ' over'
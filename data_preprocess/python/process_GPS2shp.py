# -*- coding:gb2312 -*-

import arcpy, sys
import gc
from multiprocessing import Process

def GPS_2shp(GPS_date, t_i):
    outputpath = "E:\\MapMatch\\GPS2shp\\201612%d"%(GPS_date)
    FCRef = "E:\\MapMatch\\shape_output\\20161219_001.shp"
    spatRef = arcpy.SpatialReference(4326)
    for i in range(t_i, t_i + 1):
        outputname = "GPS201612%d_%02d"%(GPS_date, i)
        e12_line = []
        r_start = 48*i + 1
        r_end = 48*(i + 1)
        for j in range(r_start, r_end + 1):
            inputfile = "D:\\项目资料\\深圳数据\\出租车GPS\\%d\\201612%d_%03d.txt"%(GPS_date, GPS_date, j)
            with open(inputfile, 'r') as file:
                for line in file:
                    e12_line.append(line)
            print("201612%d_%03d.txt"%(GPS_date, j))
        print(outputname)
        FC = arcpy.CreateFeatureclass_management(outputpath, outputname, "POINT", FCRef, "", "", spatRef)
        cursor = arcpy.InsertCursor(FC, ["Field1", "Field2", "sField3", "sField4", "Field5", "Field6", "Field7", "sField8",
                                         "sField9", "sField10"])
        print(outputname  + 'input_start')
        for oneline in e12_line:
            line = oneline.split(",")
            feature = cursor.newRow()
            vertex = arcpy.CreateObject("Point")
            vertex.X = line[4]
            vertex.Y = line[5]
            feature.shape = vertex
            feature.Field1 = line[0]
            feature.Field2 = line[1]
            feature.sField3 = line[2]
            feature.sField4 = line[3]
            feature.Field5 = line[4]
            feature.Field6 = line[5]
            feature.Field7 = line[6]
            feature.sField8 = line[7]
            feature.sField9 = line[8]
            feature.sField10 = line[9]
            cursor.insertRow(feature)
        print('Finish Projection:', outputname)
        del cursor
        del e12_line
        gc.collect()

if __name__ == '__main__':
    for i in range(6):
        p = Process(target=GPS_2shp, args=(21,i,))
        p.start()
        p.join()

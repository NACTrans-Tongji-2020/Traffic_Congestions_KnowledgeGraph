# -*- coding:gb2312 -*-

import arcpy

outputpath = r"C:\Users\Zero Yi\Documents\L\test"

FCRef = r"C:\Users\Zero Yi\Documents\L\test\source001.shp"
spatRef = arcpy.SpatialReference(4326) #y������ĳ��GPS�Ĺ淶��@11/17

for i in range(24):
    outputname = "GPS20161219_%02d"%(i)
    e12_line = []
    r_start = 12*i + 1
    r_end = 12*(i + 1)
    for j in range(r_start, r_end + 1):
        inputfile = "D:\\��Ŀ����\\��������\\���⳵GPS\\�ϲ�\\20161219\\20161219_%03d.txt"%(j) #GPS��������
        with open(inputfile, 'r') as file:
            for line in file:
                e12_line.append(line) #��ÿһ�е������
        #print("20161219_%03d.txt"%(j))
    #print(outputname)
    FC = arcpy.CreateFeatureclass_management(outputpath, outputname, "POINT", FCRef, "", "", spatRef) #����shp�����ﴴ���ļ���
    # CreateFeatureclass�С�����Ҫ���ࡱ�����ļ����д˹��߽����� shapefile��
    cursor = arcpy.InsertCursor(FC, ["Field1", "Field2", "Field3", "Field4", "Field5", "Field6", "Field7", "Field8",
                                     "Field9", "Field10"]) #����µ����ԣ�@11/17
    print(outputname  + 'input_start')
    # for oneline in allLine:
    for oneline in e12_line:
        line = oneline.split(",") #ȡ����Ϊ�ָ���
        newRow = cursor.newRow() #�������ж���
        vertex = arcpy.CreateObject("Point")
        vertex.X = line[4] #������
        vertex.Y = line[5] #��ά��
        newRow.shape = vertex
        newRow.Field1 = line[0]
        newRow.Field2 = line[1]
        newRow.Field3 = line[2]
        newRow.Field4 = line[3]
        newRow.Field5 = line[4]
        newRow.Field6 = line[5]
        newRow.Field7 = line[6]
        newRow.Field8 = line[7]
        newRow.Field9 = line[8]
        newRow.Field10 = line[9]
        cursor.insertRow(newRow) #��������
    print('Finish Projection:', outputname)
    del cursor
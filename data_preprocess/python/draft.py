# -*- coding:gb2312 -*-

# for i in range(84,86):
#     inputpath = 'GPS20161219_0%02d.shp' % (i)
#     print inputpath

# import arcpy
#
# print 'import over'
#
# line = "20161219,65457,H,��BM21U6,114.115540,22.544085,0.0,230,0,1".split(',')
# vertex = arcpy.CreateObject("Point")
# vertex.X = line[4]
# vertex.Y = line[5]
# print(dir(vertex))

# -*- coding:gb2312 -*-

import arcpy
import time

st = time.time()
outputpath = r"C:\Users\Zero Yi\Documents\L\test"

FCRef = r"C:\Users\Zero Yi\Documents\L\test\source\001.shp"
spatRef = arcpy.SpatialReference(4326) #y������ĳ��GPS�Ĺ淶��@11/17

# for i in range(24):
outputname = "GPS20161219_085"
e12_line = []


inputfile = r"C:\Users\Zero Yi\Documents\L\test\source\20161219_085.txt" #GPS��������
with open(inputfile, 'r') as file:
    for line in file:
        e12_line.append(line)

FC = arcpy.CreateFeatureclass_management(outputpath, outputname, "POINT", FCRef, "DISABLED", "DISABLED", spatRef) #����shp�����ﴴ���ļ���
# CreateFeatureclass�С�����Ҫ���ࡱ�����ļ����д˹��߽����� shapefile��
# cursor = arcpy.InsertCursor(FC, ["Field1", "Field2", "Field3", "Field4", "Field5", "Field6", "Field7", "Field8",
#                                  "Field9", "Field10"]) #����µ����ԣ�@11/17
cursor = arcpy.InsertCursor(FC, spatRef) #�Ķ��˺�һ�������������ArcGis�д�ʱ�����о���@11/19
print(outputname  + 'input_start')
# for oneline in allLine:
for oneline in e12_line:
    line = oneline.split(",") #ȡ����Ϊ�ָ���
    feature = cursor.newRow() #�������ж���
    vertex = arcpy.CreateObject("Point")
    vertex.X = line[4] #������
    vertex.Y = line[5] #��ά��
    feature.shape = vertex
    feature.Date = line[0]
    feature.Unknown1 = line[1]
    feature.Letter = line[2]
    feature.Plate = line[3]
    feature.Longitude = line[4]
    feature.Latitude = line[5]
    feature.Unknown2 = line[6]
    feature.Unknown3 = line[7]
    feature.Unknown4 = line[8]
    feature.Unknown5 = line[9]
    # feature.setValue("Unknown4", 233)
    # feature.Field1 = line[0]
    # feature.Field2 = line[1]
    # feature.Field3 = line[2]
    # feature.Field4 = line[3]
    # feature.Field5 = line[4]
    # feature.Field6 = line[5]
    # feature.Field7 = line[6]
    # feature.Field8 = line[7]
    # feature.Field9 = line[8]
    # feature.Field10 = line[9]
    cursor.insertRow(feature) #��������
print('Finish Projection:', outputname)
del cursor
print time.time()-st

# over

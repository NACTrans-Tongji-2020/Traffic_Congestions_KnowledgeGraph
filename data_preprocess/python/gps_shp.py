# -*- coding:gb2312 -*-

import arcpy

outputpath = r"C:\Users\Zero Yi\Documents\L\test"

FCRef = r"C:\Users\Zero Yi\Documents\L\test\source001.shp"
spatRef = arcpy.SpatialReference(4326) #y：这是某种GPS的规范？@11/17

for i in range(24):
    outputname = "GPS20161219_%02d"%(i)
    e12_line = []
    r_start = 12*i + 1
    r_end = 12*(i + 1)
    for j in range(r_start, r_end + 1):
        inputfile = "D:\\项目资料\\深圳数据\\出租车GPS\\合并\\20161219\\20161219_%03d.txt"%(j) #GPS数据输入
        with open(inputfile, 'r') as file:
            for line in file:
                e12_line.append(line) #把每一行单独添加
        #print("20161219_%03d.txt"%(j))
    #print(outputname)
    FC = arcpy.CreateFeatureclass_management(outputpath, outputname, "POINT", FCRef, "", "", spatRef) #创建shp，这里创建文件！
    # CreateFeatureclass叫“创建要素类”，在文件夹中此工具将创建 shapefile。
    cursor = arcpy.InsertCursor(FC, ["Field1", "Field2", "Field3", "Field4", "Field5", "Field6", "Field7", "Field8",
                                     "Field9", "Field10"]) #添加新的属性？@11/17
    print(outputname  + 'input_start')
    # for oneline in allLine:
    for oneline in e12_line:
        line = oneline.split(",") #取逗号为分隔符
        newRow = cursor.newRow() #创建空行对象
        vertex = arcpy.CreateObject("Point")
        vertex.X = line[4] #东经度
        vertex.Y = line[5] #北维度
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
        cursor.insertRow(newRow) #插入新行
    print('Finish Projection:', outputname)
    del cursor
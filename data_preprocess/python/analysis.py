# -*- coding:gb2312 -*-
import arcpy
from arcpy import env
import time

t1 = time.time()
# env.workspace = r'C:\Users\Zero Yi\Documents\L\MapMatch\bh.gdb'
env.workspace = r'C:\Users\Zero Yi\Documents\L\bh.gdb'

print("Intersect_analysis_151 start")
# for i in range(84,86):
# print("input GPSdata:GPS20161219_%02d"%(i))
print("input GPSdata")
# 数据导入
inputpath = r'C:\Users\Zero Yi\Documents\L\test\GPS20161219_085_v2.shp'
# outputpath_141 = 'E:/MapMatch/Intersect_analysis/bh_141/bh141_20161219_%02d'%(i)
outputpath_151 = r'C:\Users\Zero Yi\Documents\L\Intersect_analysis\bh_151\GPS20161219_085.shp'
# outputpath_142 = 'E:/MapMatch/Intersect_analysis/bh_142/bh142_20161219_%02d'%(i)

# 算覆盖点的时候是用buffer算
# inFeatures_141 = [inputpath, 'buffer_141']
inFeatures_151 = [inputpath, r'C:\Users\Zero Yi\Documents\L\buffer_output\buffer.shp']
# inFeatures_142 = [inputpath, 'buffer_142']
t2 = time.time()
print t2-t1
#Intersect_analysis
# 直接被buffer覆盖的点算入
print 'Intersect_analysis_151'
arcpy.Intersect_analysis(inFeatures_151, outputpath_151, 'ALL', '#', 'INPUT')
# print 'Intersect_analysis_142'
# arcpy.Intersect_analysis(inFeatures_142, outputpath_142, 'ALL', '#', 'INPUT')
t3 = time.time()
print t3-t2
# Near_analysis
# crosspath_141 = 'E:/MapMatch/Intersect_analysis/bh_141/bh141_20161219_%02d.shp'%(i)
crosspath_151 = r'C:\Users\Zero Yi\Documents\L\Intersect_analysis\bh_151\GPS20161219_085.shp' # 应该就是上面的output
# crosspath_142 = 'E:/MapMatch/Intersect_analysis/bh_142/bh142_20161219_%02d.shp'%(i)

# 归总到路上的时候是直接归总到全路上
print 'Near_analysis_151'
arcpy.Near_analysis(crosspath_151, r'C:\Users\Zero Yi\Documents\L\bh_dissolve\test_dissolved.shp', '#', 'LOCATION', 'ANGLE', 'PLANAR')
# print 'Near_analysis_142'
# arcpy.Near_analysis(crosspath_142, 'bh_142', '#', 'LOCATION', 'ANGLE', 'PLANAR')
# print('Finish Projection:'+ " GPS20161219_%02d"%(i))
print "test over"
t4 = time.time()
print t4-t3
print t4-t1
# del inFeatures_141
# del inFeatures_142




"""
dic = {}
cursor = arcpy.da.SearchCursor('E:/mapmatching/crossings_test.shp', ['FID','NEAR_X','NEAR_Y'])
for row in cursor:
    dic[row[0]] = [row[1],row[2]]
del cursor
del row

cursor = arcpy.da.UpdateCursor('E:/mapmatching/crossings_test.shp',['FID', 'SHAPE@XY'])
for row in cursor:
    row[1] = dic[row[0]]
    cursor.updateRow(row)
del cursor
del row
"""
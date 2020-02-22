import arcpy
from arcpy import env
# env.workspace = r'E:/MapMatch/bh.gdb'
# env.workspace = r'C:\Users\Zero Yi\Documents\L\bh.gdb'
# print "workspace over"
# print 'Buffer_141'
# arcpy.Buffer_analysis('bh_141', 'E:/MapMatch/buffer_output/buffer', '15 Meters', 'FULL', 'ROUND', 'ALL', '#', 'PLANAR')


arcpy.Buffer_analysis(r"C:\Users\Zero Yi\Documents\L\data_preprocess\bh_dissolve\bh_151.shp", r'C:\Users\Zero Yi\Documents\L\data_preprocess\buffer_output\buffer_151.shp', '15 Meters', 'FULL', 'ROUND', 'ALL', '#', 'PLANAR')
arcpy.Buffer_analysis(r"C:\Users\Zero Yi\Documents\L\data_preprocess\bh_dissolve\bh_152.shp", r'C:\Users\Zero Yi\Documents\L\data_preprocess\buffer_output\buffer_152.shp', '15 Meters', 'FULL', 'ROUND', 'ALL', '#', 'PLANAR')

print "test over"
# print 'Buffer_142'
# arcpy.Buffer_analysis('bh_142', 'E:/MapMatch/buffer_output/buffer', '15 Meters', 'FULL', 'ROUND', 'ALL', '#', 'PLANAR')
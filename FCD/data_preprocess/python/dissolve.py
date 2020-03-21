# -*- coding:gb2312 -*-
import arcpy
from arcpy import env
# env.workspace = r'E:\\mapmatching\\bh.gdb'
print "import over"
# env.workspace = r'C:\Users\Zero Yi\Documents\L\data_process\bh.gdb'
print "workspace over"

arcpy.Dissolve_management(r"C:\Users\Zero Yi\Documents\L\data_preprocess\bh_dissolve\BeiHuanDaDao.shp",  r"C:\Users\Zero Yi\Documents\L\data_preprocess\bh_dissolve\BeiHuanDaDao2.shp",
                          "AB_ROADNO", "", "SINGLE_PART","DISSOLVE_LINES")
print "test over"
#arcpy.Dissolve_management("bh_142", "E:\\mapmatching\\bh_dissolve\\bh142_dissolved",
                          #"AB_ROADNO", "", "SINGLE_PART","DISSOLVE_LINES")
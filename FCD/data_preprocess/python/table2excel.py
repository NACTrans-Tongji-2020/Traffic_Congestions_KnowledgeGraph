import arcpy
import time

st = time.time()

inputpath = r'C:\Users\Zero Yi\Documents\L\Intersect_analysis\bh_151\GPS20161219_085.dbf'

outputpath_141 = r'C:\Users\Zero Yi\Documents\L\Excel\bh_151\GPS20161219_085_v2.xls'
arcpy.TableToExcel_conversion(inputpath, outputpath_141)

print time.time()-st
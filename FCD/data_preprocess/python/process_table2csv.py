import arcpy
from multiprocessing import Process


def dbf_2csv(GPS_date):
    for i in range(6):
        inputpath_141 = 'E:/MapMatch/Intersect_analysis/bh_141/201612%d/bh141_201612%d_%02d.dbf' % (GPS_date, GPS_date, i)
        outputpath_141 = 'E:/MapMatch/dbf_2csv/bh_141/201612%d'%(GPS_date)
        inputpath_142 = 'E:/MapMatch/Intersect_analysis/bh_142/201612%d/bh142_201612%d_%02d.dbf' % (GPS_date, GPS_date, i)
        outputpath_142 = 'E:/MapMatch/dbf_2csv/bh_142/201612%d'%(GPS_date)
        arcpy.TableToTable_conversion(inputpath_141, outputpath_141, 'bh141_201612%d_%02d.csv' % (GPS_date, i))
        arcpy.TableToTable_conversion(inputpath_142, outputpath_142, 'bh142_201612%d_%02d.csv' % (GPS_date, i))

if __name__ == '__main__':
    for j in range(20, 24):
        p = Process(target=dbf_2csv, args=(j,))
        p.start()
        p.join()
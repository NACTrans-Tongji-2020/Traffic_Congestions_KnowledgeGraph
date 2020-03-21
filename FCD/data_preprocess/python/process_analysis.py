import arcpy
from arcpy import env
from multiprocessing import Process

env.workspace = r'E:/MapMatch/bh.gdb'

def GPS_road_analysis(GPS_date):
    print("Intersect_analysis_ start")
    for i in range(6):
        print("input GPSdata:GPS201612%d_%02d"%(GPS_date, i))
        inputpath = 'E:/MapMatch/GPS2shp/201612%d/GPS201612%d_%02d.shp'%(GPS_date, GPS_date, i)
        outputpath_141 = 'E:/MapMatch/Intersect_analysis/bh_141/201612%d/bh141_201612%d_%02d'%(GPS_date, GPS_date, i)
        outputpath_142 = 'E:/MapMatch/Intersect_analysis/bh_142/201612%d/bh142_201612%d_%02d'%(GPS_date, GPS_date, i)
        inFeatures_141 = [inputpath, 'buffer_141']
        inFeatures_142 = [inputpath, 'buffer_142']

        #Intersect_analysis
        print 'Intersect_analysis_141'
        arcpy.Intersect_analysis(inFeatures_141, outputpath_141, 'ALL', '#', 'INPUT')
        print 'Intersect_analysis_142'
        arcpy.Intersect_analysis(inFeatures_142, outputpath_142, 'ALL', '#', 'INPUT')

        # Near_analysis
        crosspath_141 = 'E:/MapMatch/Intersect_analysis/bh_141/201612%d/bh141_201612%d_%02d.shp'%(GPS_date, GPS_date, i)
        crosspath_142 = 'E:/MapMatch/Intersect_analysis/bh_142/201612%d/bh142_201612%d_%02d.shp'%(GPS_date, GPS_date, i)
        print 'Near_analysis_141'
        arcpy.Near_analysis(crosspath_141, 'bh141_dissolved', '#', 'LOCATION', 'ANGLE', 'PLANAR')
        print 'Near_analysis_142'
        arcpy.Near_analysis(crosspath_142, 'bh142_dissolved', '#', 'LOCATION', 'ANGLE', 'PLANAR')
        print('Finish Projection:'+ " GPS201612%d_%02d"%(GPS_date, i))
        del inFeatures_141
        del inFeatures_142


if __name__ == '__main__':
    for i in range(20, 24):
        p = Process(target=GPS_road_analysis, args=(i,))
        p.start()
        p.join()
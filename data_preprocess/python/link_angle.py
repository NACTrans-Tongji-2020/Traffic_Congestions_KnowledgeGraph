import arcpy
import csv
from math import radians, cos, sin, degrees, atan2

fc_151 = r"C:\Users\Zero Yi\Documents\L\data_preprocess\bh_fenduan\bh_151.shp"
fc_152 = r"C:\Users\Zero Yi\Documents\L\data_preprocess\bh_fenduan\bh_152.shp"
print "workspace over"

def getDegree(lonA, latA, lonB, latB):
    # Args:point p1(lonA, latA)point p2(lonB, latB)
    # Returns:bearing between the two GPS points,default: the basis of heading direction is north
    radLatA = radians(latA)
    radLonA = radians(lonA)
    radLatB = radians(latB)
    radLonB = radians(lonB)
    dLon = radLonB - radLonA
    y = sin(dLon) * cos(radLatB)
    x = cos(radLatA) * sin(radLatB) - sin(radLatA) * cos(radLatB) * cos(dLon)
    brng = degrees(atan2(y, x))
    brng = float((brng + 360.0) % 360.0)
    return brng


ls = []
with arcpy.da.SearchCursor(fc_151, ["SHAPE@","FID"]) as cursor:
    for row in cursor:
        xL, yL = row[0].firstPoint.X, row[0].firstPoint.Y
        xR, yR = row[0].lastPoint.X, row[0].lastPoint.Y
        LR_degree = getDegree(xL, yL, xR, yR)
        FID = int(row[1]) + 1
        ls.append([FID, xL, yL, xR, yR, LR_degree])

with open(r'C:\Users\Zero Yi\Documents\L\data_preprocess\bh_fenduan\151_degree.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile)
    for row in ls:
        writer.writerow(row)

print "test over"
#142
# ls = []
# with arcpy.da.SearchCursor(fc_142, ["SHAPE@","FID"]) as cursor:
#     for row in cursor:
#         #print(1)
#         xL, yL = row[0].firstPoint.X, row[0].firstPoint.Y
#         xR, yR = row[0].lastPoint.X, row[0].lastPoint.Y
#         LR_degree = getDegree(xL, yL, xR, yR)
#         FID = int(row[1]) + 1
#         ls.append([FID, xL, yL, xR, yR, LR_degree])
#
# with open('E:\\mapmatching\\bh_dissolve\\degree\\142_dissolved_degree.csv', 'wb') as csvfile:
#     writer  = csv.writer(csvfile)
#     for row in ls:
#         writer.writerow(row)
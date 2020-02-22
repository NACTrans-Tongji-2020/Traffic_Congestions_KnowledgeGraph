# 这个script用来提取分段的shp文件里面各个路段的起始和终止坐标
# 需要geopandas
# 我是使用ArcGis自带的python2运行的这个script，所以这不算是工程里的文件
# 况且我的python3也没有安装geopandas
# 只是因为也是这个步骤里的，所以放在这里

import geopandas as gp
import pandas as pd

shpfile1 = r"C:\Users\Zero Yi\Documents\L\data_preprocess\bh_fenduan\bh_151.shp"
shpfile2 = r"C:\Users\Zero Yi\Documents\L\data_preprocess\bh_fenduan\bh_152.shp"

dataframe151 = pd.DataFrame()
dataframe152 = pd.DataFrame()

geodf = gp.GeoDataFrame.from_file(shpfile1)
geodf2 = gp.GeoDataFrame.from_file(shpfile2)

hX = []  # 分别是起点的经度，起点的纬度，终点的经度，终点的纬度
hY = []
eX = []
eY = []
for row in geodf['geometry'].iteritems():
     hX.append(row[1].coords[0][0])
     hY.append(row[1].coords[0][1])
     eX.append(row[1].coords[-1][0])
     eY.append(row[1].coords[-1][1])
dataframe151['headCoordsX'] = hX
dataframe151['headCoordsY'] = hY
dataframe151['endCoordsX'] = eX
dataframe151['endCoordsY'] = eY

hX = []  # 分别是起点的经度，起点的纬度，终点的经度，终点的纬度
hY = []
eX = []
eY = []
for row in geodf2['geometry'].iteritems():
     hX.append(row[1].coords[0][0])
     hY.append(row[1].coords[0][1])
     eX.append(row[1].coords[-1][0])
     eY.append(row[1].coords[-1][1])
dataframe152['headCoordsX'] = hX
dataframe152['headCoordsY'] = hY
dataframe152['endCoordsX'] = eX
dataframe152['endCoordsY'] = eY

path = r'C:\Users\Zero Yi\Documents\L\data_preprocess\bh_fenduan\bh_151.csv'
dataframe151.to_csv(path)
path = r'C:\Users\Zero Yi\Documents\L\data_preprocess\bh_fenduan\bh_152.csv'
dataframe152.to_csv(path)

# 实测保存成csv比xls节约一些空间
# 最后手动把坐标放到王子给的路段命名exl里面去

# 此文件下面放的是所有有关于道路分析的代码
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from math import ceil
import pymongo

def timeSliceAnalysis(df, columnPlate = 'Plate', columnTime = 'Time'):
    '''

    :param df:          输入的浮动车数据，以DataFrame形式
    :param columnPlate: 车牌字段的名称，默认是'Plate'
    :param columnTime:  浮动车更新时间字段的名称，默认是'Time'
    :return:            返回两个列表，plates和diffs分别是所有的车牌和对应的数据更新时间间隔
    '''

    plates = []
    diffs = []
    for name, group in df.groupby(columnPlate):
        if len(group) > 1:
            time1 = group[columnTime].as_matrix()
            time2 = np.append(time1, 0)[1:]
            diff = abs(time1 - time2)

            diffmin = np.min(diff)  # 取最小的，当成是更新时间。由于已经去重了，所以按理说不应该有0
            if diffmin < 120:  # 超过120S的更新的，就当不是GPS的更新，而是车辆只在道路上短暂的停留或者是噪声
                plates.append(name)
                diffs.append(diffmin)
                print('Joined:', name, 'Period', diffmin)
            else:
                print('Excluded:', name, 'Period', diffmin)

    return plates, diffs

def hist(datalist, bins = 12, range = None, density = True):
    '''
    用来分析浮动车的GPS数据更新时间的分布情况，根据20161219日的数据来看，
    超过90%的浮动车更新时间在60s之内，所以时间片取为60s

    :param datalist:    需要做累积直方图的列表
    :param bins:        区间个数，默认12
    :param range:       总共的范围，列表，默认是[0,120]，也就是0-120s
    :param density:     是计算频率还是频数，默认频率(True)
    :return:    返回两个数组，分别是区间的边界值，和到各个区间时累积的频率/频数
    '''
    if range is None:
        range = [0, 120]

    n, binBoundaries, _ = plt.hist(datalist, bins, range, density, cumulative=True)
    plt.grid()
    plt.show()

    return n, binBoundaries

class session:
    '''
    打算初级尝试使用面向对象的思想来实现入库的动作。
    '''
    def __init__(self):
        self.client = None
        self.database = None
        self.collection = None
        self.dataframe = pd.DataFrame()

    def connetMongo(self, url='mongodb://localhost:27017'):
        self.client = pymongo.MongoClient(url)  # 默认是使用本地客户端

    def connetDatabase(self, databaseName):
        # if self.client is None:
        #     raise Exception('未连接MongoDB客户端！')
        self.database = self.client[databaseName]

    def connetCollection(self, collectionName):
        # if self.client is None:
        #     raise Exception('未连接MongoDB客户端！')
        # elif self.database is None:
        #     raise Exception('未指定数据库！')
        self.collection = self.database[collectionName]

    def addRoadNode(self, date, startTime, coreX, coreY,  averageSpeed, conjunctionLevel):
        '''
        向指定的数据库的指定集合中添加文档。针对的是路段节点。

        :param core:            路段的拥堵重心
        :param startTime:       路段时间片起始时间戳
        :param averageSpeed:    路段的平均速度
        :param conjunctionLevel: 路段的拥堵等级
        :return:
        '''
        dict = {
            'date': date,
            'startTime': startTime,
            'coreX': coreX,
            'coreY': coreY,
            'averageSpeed': averageSpeed,
            'conjunctionLevel': conjunctionLevel
        }
        self.collection.insert_one(dict)

    def loadDataframe(self, df):
        self.dataframe = df

    def outputDataframe(self, path, df=None):
        if df is None:
            df = self.dataframe
        df.to_csv(path)

    def merge(self, exlPath, cols=None):
        '''
        :param exlPath:  需要合并的exl所在的文件夹
                cols:     指定读取哪些字段，建议是以列序号为元素的列表，比如[2,3,4]（第一列序号是0）
        :return: 返回一个DataFrame类型的给到会话的主表格，所有数据合并并且去重之后的
        '''
        for files in os.listdir(exlPath):
            # print(files)
            file = exlPath + files
            temp = pd.read_excel(file, index_col=0, usecols=cols)
            self.dataframe = self.dataframe.append(temp, ignore_index=True)
        self.dataframe = self.dataframe.drop_duplicates()

    def average(self, df=None, col='Speed'):
        '''
        输入一个表格，计算里面所有车辆的某个字段的均值，默认是速度'Speed'字段。
        速度存储在'Speed'字段里面。

        :param df:输入的数据表格，要求是pandas.DataFrameObject，默认处理的是此次会话处理的主表格。
        :return: 均值
        '''
        if df is None:
            df = self.dataframe
        aves = df[col].values
        return np.mean(aves)

    def timeSlicing(self, df=None, replaceDF=True):
        '''
        对数据进行时间片划分，默认时间片大小60s，增加一个字段'SliceStamp'，存放时间片开始的时间戳，格式是小时分钟，比如
        一个时间戳是1423，说明其处于14:23-14:24的时间片内。
        由于默认的时间片大小60s支持一种取巧的划分方式，所以下面就没有用到period了。

        :param df:      输入的数据，Pandas.DataFrameObject，默认处理的是此次会话处理的主表格。
        :param replaceDF: 是否要将处理过后的DataFrame对象替换入此次会话的主表格，默认是进行替换。
        :return:        处理过后的DataFrame对象
        '''
        if df is None:
            df = self.dataframe

        temp = df['Time'].values / 100
        df['SliceStamp'] = temp.astype(int)  # 效果类似于向下取整，以整数保存比浮点更加节省空间
        if replaceDF is True:
            self.dataframe = df  # 处理过后的结果替换入主表格

        return df

    def calculateVdk(self, List):
        '''
        根据给定的数据表的平均速度确定自由通行速度。
        根据观察，凌晨的时候有一些车速度为0，估计是停在路边休息。因此这边把0值全部剔除。

        :param List:    所有参与计算的数据表
        :return:        返回计算得到的Vdk
        '''
        speeds = pd.Series()
        for excelfile in List:
            df = pd.read_excel(excelfile)
            speeds = speeds.append(df['Speed'], ignore_index=True)
        filterList = speeds.isin([0])  # 剔除0值
        return np.mean(speeds[~filterList].values)

    def analysis(self, Vdk, df=None, threshold=4):
        '''
        用来对数据进行分析，拥堵情况等。对于符合的情况，加载到一个数据表中返回。
        返回的数据表字段为['Date', 'NEAR_FID', 'SliceStamp', 'CoreLongitude', 'Corelatitude', 'Vk', 'Level']
        返回的date方便保存的csv命名

        :param df:      等待分析的数据，DataFrame类型的数据，默认处理的是此次会话的主表格。
        :param Vdk:     自由流速，取若干个凌晨时段路段上所有样本车辆的速度均值。
        :param threshold: 入库的阈值，默认为4，即不小于4才入库
        :return:
        '''
        if df is None:
            df = self.dataframe

        resultDF = pd.DataFrame(
            columns=['Date', 'NEAR_FID', 'SliceStamp', 'CoreLongitude', 'CoreLatitude', 'Vk', 'Level', 'numberOfCars'])

        for name1, group_seg in df.groupby('NEAR_FID'):  # 按照路段对数据进行分组
            for name2, group_slice in group_seg.groupby('SliceStamp'):  # 按照时间片对数据再进行分组
                Vk = self.average(group_slice)
                if Vk == 0:  #  防止分母为零
                    Vk = 0.01
                ratio = Vdk / Vk
                indicate, level = self.TPI(ratio)
                if level >= threshold:
                    coreLongitude = self.average(group_slice, 'Longitude')
                    coreLatitude = self.average(group_slice, 'Latitude')
                    resultDF = resultDF.append(
                        {'Date':group_slice['Date'].iloc[0], 'NEAR_FID':name1, 'SliceStamp':name2, 'CoreLongitude':coreLongitude,
                         'CoreLatitude':coreLatitude, 'Vk':Vk, 'Level':level, 'numberOfCars': len(group_slice)}, ignore_index=True)

        return resultDF

    def TPI(self, ratio):
        '''
        该函数实现了由行程时间比，根据专家打分确定的换算关系，得到道路交通运行指数TPI，与相对应的拥堵等级判定
        level的1-5分别对应的是
        1：畅通
        2：基本畅通
        3：缓行
        4：轻度拥堵
        5：拥堵

        :param ratio:   特定时间段内的行程时间比
        :return:        道路交通运行指数indicate，拥堵等级level
        '''

        if ratio <= 0:
            print(ratio)
            raise Exception('行程时间比为非正数，请检查！')
        elif ratio <= 1:
            indicate = 0
        elif ratio <= float(4/3):
            indicate = 4 - (4 / ratio)
        elif ratio <= float(20/11):
            indicate = 4.75 - 5 / ratio
        elif ratio <= 2.5:
            indicate = (17 - 20 / ratio)/3
        else:
            indicate = 5 - 5/ratio

        if indicate < 0:
            raise Exception("指标非正，具体为%.2f" % indicate)
        elif indicate > 5:
            raise Exception("指标爆5，具体为%.2f，此时ratio是%.2f" % (indicate,ratio))
        elif indicate == 0:
            level = 1
        else:
            level = ceil(indicate)
        return indicate, level


    def bulkAdding(self, df=None):
        '''

        :param df:
        :return:
        '''
        if df is None:
            df = self.dataframe

        for name1, group_seg in df.groupby('NEAR_FID'):  # 按照路段对数据进行分组
            self.connetCollection(str(name1))
            for index, row in group_seg.iterrows():
                date = row['Date']
                coreX = row['NEAR_X']
                coreY = row['NEAR_Y']
                startTime = row['SliceStamp']
                averageSpeed = row['Vk']
                conjunctionLevel = row['Level']
                self.addRoadNode(date, startTime, coreX, coreY, averageSpeed, conjunctionLevel)

        print("Bulkadding finished.")


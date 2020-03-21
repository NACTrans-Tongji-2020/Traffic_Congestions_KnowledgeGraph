import pymongo
import pandas as pd

def connet():
    '''
    连接到MongoDB的服务器，并返回客户端。连接的URL解释如下：
    mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]
    -   mongodb:// 这是固定的格式，必须要指定。
    -   username:password@ 可选项，如果设置，在连接数据库服务器之后，驱动都会尝试登陆这个数据库
    -   host1 必须的指定至少一个host, host1 是这个URI唯一要填写的。它指定了要连接服务器的地址。如果要连接复制集，请指定多个主机地址。
    -   portX 可选的指定端口，如果不填，默认为27017
    -   /database 如果指定username:password@，连接并验证登陆指定数据库。若不指定，默认打开 test 数据库。
    -   ?options 是连接选项。如果不使用/database，则前面需要加上/。所有连接选项都是键值对name=value，键值对之间通过&或;（分号）隔开

    :return: myclient
    '''

    myclient = pymongo.MongoClient('mongodb://localhost:27017') # 默认是使用本地客户端

    return myclient

def roadCollectionCreate(database, segmentList, segmentNames, headCoordsX, headCoordsY, endCoordsX, endCoordsY):
    '''
    该函数会根据输入的列表，在给定的数据库中生成数量等同于segmentList列表长度的集合，各集合名称即为segmentList中各元素
    每个集合中会生成一个文档，记录该路段的代号、名称、起始坐标、终止坐标这些属性

    :param
    database:       指定的MongoDB数据库
    segmentList:    所有路段代号的列表，比如['SimonAve1','SimonAve2','JordanSt1']，元素需要是字符串
    segmentNames:   所有路段名称的列表，顺序与上面列表对应
    headCoords:     所有路段起始坐标的列表，顺序与上面列表对应，X和Y分别代表的是经度和纬度
    endCoords:      所有路段终止坐标的列表，顺序与上面列表对应

    :return: 无
    '''

    collist = database.list_collection_names() # 用来防止重复创建

    index = 0 # 用来检索对应的名称

    for segment in segmentList:
        if segment in collist:
            print("Skipped:", segment)
            index += 1
            continue
        else:
            collection = database[segment]
            infoDict = {
                'code': segment,
                'name': segmentNames[index],
                'headCoordinateX': headCoordsX[index],
                'endCoordinateX': endCoordsX[index],
                'headCoordinateY': headCoordsY[index],
                'endCoordinateY': endCoordsY[index],
                # 'traffidAttribute':,
                }
            collection.insert_one(infoDict)
            print("Created:", infoDict['code'])
            index += 1

if __name__ == '__main__':
    # myclient = connet()
    # traffic151DB = myclient['traffic151DB']
    # bh151Df = pd.read_excel('Bh_151.xlsx')
    # segmentList = bh151Df['FID'].values.tolist()
    # segmentList = [str(x) for x in segmentList]
    # segmentNames = bh151Df["路段名"].tolist()
    # headCoordsX = bh151Df["headCoordsX"].tolist()
    # headCoordsY = bh151Df["headCoordsY"].tolist()
    # endCoordsX = bh151Df["endCoordsX"].tolist()
    # endCoordsY = bh151Df["endCoordsY"].tolist()
    # roadCollectionCreate(traffic151DB, segmentList, segmentNames, headCoordsX, headCoordsY, endCoordsX, endCoordsY)

    myclient = connet()
    traffic151DB = myclient['traffic152DB']
    bh151Df = pd.read_excel('Bh_152.xlsx')
    segmentList = bh151Df['FID'].values.tolist()
    segmentList = [str(x) for x in segmentList]
    segmentNames = bh151Df["路段名"].tolist()
    headCoordsX = bh151Df["headCoordsX"].tolist()
    headCoordsY = bh151Df["headCoordsY"].tolist()
    endCoordsX = bh151Df["endCoordsX"].tolist()
    endCoordsY = bh151Df["endCoordsY"].tolist()
    roadCollectionCreate(traffic151DB, segmentList, segmentNames, headCoordsX, headCoordsY, endCoordsX, endCoordsY)

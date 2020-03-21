import pymongo

def addRoadNode(database, roadSegmentID, core, startTime, averageSpeed, conjunctionLevel):
    '''
    向指定的数据库的指定集合中添加文档。针对的是路段节点。

    :param database:        指定的数据库，这里给的应该是pynongo里面的数据库对象
    :param roadSegmentID:   指定的路段ID，这里就是集合的名字
    :param core:            路段的拥堵重心
    :param startTime:       路段时间片起始时间戳
    :param averageSpeed:    路段的平均速度
    :param conjunctionLevel: 路段的拥堵等级
    :return:
    '''

    collection = database[roadSegmentID]
    dict = {
        'core': core,
        'startTime': startTime,
        'averageSpeed': averageSpeed,
        'conjunctionLevel': conjunctionLevel
    }
    collection.insert_one(dict)

def modifyRoadNode(database, roadSegmentID, **query, **dest):
    '''
    替换某个节点的某个数据
    :param database:
    :param roadSegmentID:
    :param query:   满足的条件，输入格式类似于Time = 123000
    :param dest:    想要修改成的东西，输入格式类似于Speed = 30
    :return:
    '''
    collection = database[roadSegmentID]
    collection.update_one(query, {'$set': dest})


if __name__ == '__main__':
    pass


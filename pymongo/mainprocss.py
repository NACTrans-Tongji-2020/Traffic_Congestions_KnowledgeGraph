import analysis
import pandas as pd

if __name__ == '__main__':
    # 开启一个处理会话
    mysess = analysis.session()

    # 计算自由流通速度，这些数据的采样时间都是在凌晨2:30左右
    # bh151filelist = [
    #     r"C:\Users\Zero Yi\Documents\L\data_preprocess\Excel\bh151\19\20161219_030.xls",
    #     r"C:\Users\Zero Yi\Documents\L\data_preprocess\Excel\bh151\20\20161220_030.xls",
    #     r"C:\Users\Zero Yi\Documents\L\data_preprocess\Excel\bh151\21\20161221_030.xls",
    #     r"C:\Users\Zero Yi\Documents\L\data_preprocess\Excel\bh151\22\20161222_030.xls",
    #     r"C:\Users\Zero Yi\Documents\L\data_preprocess\Excel\bh151\23\20161223_030.xls"
    #             ]
    # bh152filelist = [
    #     r"C:\Users\Zero Yi\Documents\L\data_preprocess\Excel\bh152\19\20161219_030.xls",
    #     r"C:\Users\Zero Yi\Documents\L\data_preprocess\Excel\bh152\20\20161220_030.xls",
    #     r"C:\Users\Zero Yi\Documents\L\data_preprocess\Excel\bh152\21\20161221_030.xls",
    #     r"C:\Users\Zero Yi\Documents\L\data_preprocess\Excel\bh152\22\20161222_030.xls",
    #     r"C:\Users\Zero Yi\Documents\L\data_preprocess\Excel\bh152\23\20161223_030.xls"
    #             ]
    # bh151Vdk = mysess.calculateVdk(bh151filelist)
    # bh152Vdk = mysess.calculateVdk(bh152filelist)
    # 计算所得，方便起见直接赋值
    bh151Vdk = 64.62983995869902
    bh152Vdk = 66.39714436805923

    for i in [19,20,21,22,23]:
        mysess.loadDataframe(pd.DataFrame())  # 每次循环之前需要清空主表格

        # 进行数据的读入
        d19_path = r'C:\Users\Zero Yi\Documents\L\data_preprocess\Excel\bh151\%d\\' % i
        mysess.merge(d19_path)  # 将文件夹里面的excel全部载入会话的主表格
        mysess.timeSlicing()  # 对主表格进行时间片切分
        df = mysess.analysis(Vdk=bh151Vdk)
        path = r'C:\Users\Zero Yi\Documents\L\pymongo\excel\bh151\\'
        df.to_csv(path + str(i) + '.csv')
        print('151 %d 完成' % i)

        mysess.loadDataframe(pd.DataFrame())
        d19_path = r'C:\Users\Zero Yi\Documents\L\data_preprocess\Excel\bh152\%d\\' % i
        mysess.merge(d19_path)  # 将文件夹里面的excel全部载入会话的主表格
        mysess.timeSlicing()  # 对主表格进行时间片切分
        df = mysess.analysis(Vdk=bh152Vdk)
        path = r'C:\Users\Zero Yi\Documents\L\pymongo\excel\bh152\\'
        df.to_csv(path + str(i) + '.csv')
        print('152 %d 完成' % i)

    # 此处使用Python2处理一下重心，处理完之后走下面
    mysess.connetMongo()  # 连接数据库客户端
    mysess.connetDatabase('traffic151DB')  # 连接bh151数据库

    usecols = ['Date', 'NEAR_FID', 'SliceStamp', 'Vk', 'Level', 'NEAR_X', 'NEAR_Y']  # 过滤掉不用的字段
    df = pd.read_excel(r"C:\Users\Zero Yi\Documents\L\pymongo\gravcore\excel\bh151\19.xls", usecols=usecols)
    mysess.loadDataframe(df)
    mysess.bulkAdding()
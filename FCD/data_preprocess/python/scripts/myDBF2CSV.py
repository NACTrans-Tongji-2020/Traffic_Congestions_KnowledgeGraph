# -*- coding:gb2312 -*-
# import dbfread
#
# table = dbfread.DBF(r'C:\Users\Zero Yi\Documents\L\Intersect_analysis\bh_151\GPS20161219_085.dbf')
# https://dbfread.readthedocs.io/en/latest/

from arcpy import TableToExcel_conversion
import os

# st = time.time()
#
# inputpath = r'C:\Users\Zero Yi\Documents\L\Intersect_analysis\bh_151\GPS20161219_085.dbf'
#
# outputpath_141 = r'C:\Users\Zero Yi\Documents\L\Excel\bh_151\GPS20161219_085_v2.xls'
# arcpy.TableToExcel_conversion(inputpath, outputpath_141)

# print time.time()-st

def DBF2CSV(input_path, output_path):
    '''
    :param input_path: 待转换的dbf文件所在文件夹
    :param output_path: 生产的csv文件存放的文件夹
    :return:
    '''
    for dbffile in os.listdir(input_path):
        if os.path.splitext(dbffile)[1] == '.dbf': # 过滤其他后缀文件
            inputfile = input_path + dbffile
            outputfile = output_path + os.path.splitext(dbffile)[0] + '.xls'
            print(outputfile)
            TableToExcel_conversion(inputfile, outputfile)

if __name__ == '__main__':
    dbf_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/Intersect_analysis/bh_151/'
    csv_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/Excel/bh_151/'
    DBF2CSV(dbf_path, csv_path)

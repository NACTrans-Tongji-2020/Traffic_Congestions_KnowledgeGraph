# -*- coding:gb2312 -*-
import myDBF2CSV
import myprocess_analysis
import myprocess_GPS2shp
import angleselect

if __name__ == '__main__':
    # ��������TXT����ת����SHP
    # inshp = 'C:/Users/Zero Yi/Documents/L/data_preprocess/buffer_output/buffer.shp'
    # XMax, XMin, YMax, YMin = myprocess_GPS2shp.preprocess(inshp)
    for i in [19, 20, 21, 22, 23]:
        # txt_path = 'C:/Users/Zero Yi/Documents/L/SZ201612/19/'
        shp_path = 'C:/Users/Zero Yi/Documents/L/SZ201612/shp/%d/' % i
        # myprocess_GPS2shp.GPS_2shp(txt_path, shp_path, XMax, XMin, YMax, YMin)
        # TXT2SHPת�����

        # ---------------------- δ���Ƿ����ɸѡ
        # buffer_file = 'C:/Users/Zero Yi/Documents/L/data_preprocess/buffer_output/buffer.shp'
        # dissolved_file = 'C:/Users/Zero Yi/Documents/L/data_preprocess/bh_dissolve/test_dissolved.shp'
        #
        # # shp_path = 'C:/Users/Zero Yi/Documents/L/test/shp/'
        # dbf_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/Intersect_analysis/23/'
        #
        # myprocess_analysis.GPS_road_analysis(buffer_file, dissolved_file, shp_path, dbf_path)
        #
        # csv_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/Excel/23/'
        # myDBF2CSV.DBF2CSV(dbf_path, csv_path)
        # ----------------------------

        # ----------------------------���Ƿ����ɸѡ
        buffer_file = 'C:/Users/Zero Yi/Documents/L/data_preprocess/buffer_output/buffer_151.shp'
        # dissolved_file = 'C:/Users/Zero Yi/Documents/L/data_preprocess/bh_divided/bh_divided_151.shp'
        dissolved_file = 'C:/Users/Zero Yi/Documents/L/data_preprocess/bh_fenduan/bh_151.shp'
        # �������ƥ�����ʹ��·���� @2.18 ʹ�õ���������������·��

        dbf_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/Intersect_analysis/bh151/%d/' % i
        if i != 19:
            myprocess_analysis.GPS_road_analysis(buffer_file, dissolved_file, shp_path, dbf_path)

        output_path = r'C:\Users\Zero Yi\Documents\L\data_preprocess\Intersect_analysis\filtershp\bh151\%d\\' % i
        anglexls = 'C:\\Users\\Zero Yi\\Documents\\L\\data_preprocess\\bh_fenduan\\151_degree.csv'

        angleselect.anglesel(dbf_path, anglexls, output_path)  # ���ɵ�shp��dbf��һ���ļ�������

        csv_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/Excel/bh151/%d/' % i
        myDBF2CSV.DBF2CSV(output_path, csv_path)
        print('151 over')

        #  --------------------����bh151������bh152------------------------

        buffer_file = 'C:/Users/Zero Yi/Documents/L/data_preprocess/buffer_output/buffer_152.shp'
        dissolved_file = 'C:/Users/Zero Yi/Documents/L/data_preprocess/bh_fenduan/bh_152.shp'

        dbf_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/Intersect_analysis/bh152/%d/' % i

        myprocess_analysis.GPS_road_analysis(buffer_file, dissolved_file, shp_path, dbf_path)

        output_path = r'C:\Users\Zero Yi\Documents\L\data_preprocess\Intersect_analysis\filtershp\bh152\%d\\' % i
        anglexls = 'C:\\Users\\Zero Yi\\Documents\\L\\data_preprocess\\bh_fenduan\\152_degree.csv'

        angleselect.anglesel(dbf_path, anglexls, output_path)  # ���ɵ�shp��dbf��һ���ļ�������

        csv_path = 'C:/Users/Zero Yi/Documents/L/data_preprocess/Excel/bh152/%d/' % i
        myDBF2CSV.DBF2CSV(output_path, csv_path)

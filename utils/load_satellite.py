import numpy as np
from utils.PV_J2000_OEV import PV_J2000_OEV
from utils.read_satinfo import read_satinfo

def load_satellite():

    # 从星务读取卫星姿轨数据

    ###### hex_file = "D:\SoftWare\PythonCode\gongda_mp\data_file\pose_data0703"
    hex_file = "/home/chujiaqing/newpro/gongda_mp/data_file/pose_data0703"  # 16进制文件

    ###### satinfo_file = "D:\SoftWare\PythonCode\gongda_mp\data_file\satinfo.txt"
    satinfo_file = "/home/chujiaqing/newpro/gongda_mp/data_file/satinfo.txt"  # 输出的卫星信息文件(仅供展示)

    ###### output_file = "D:\SoftWare\PythonCode\gongda_mp\data_file\datarv.txt"
    output_file = "/home/chujiaqing/newpro/gongda_mp/data_file/datarv.txt"  # 输出的卫星信息文件(参与下面的任务规划流程)


    # 从16进制文件读取卫星全部信息
    read_satinfo(hex_file, satinfo_file, output_file)
    # 从中提取卫星位置和速度信息


    # 从data.txt加载初始轨道状态, max_rows=1限制为单星
    ####### rv0 = np.loadtxt('D:\SoftWare\PythonCode\gongda_mp\data_file\data.txt', max_rows=1)
    rv0 = np.loadtxt('/home/chujiaqing/newpro/gongda_mp/data_file/datarv.txt', max_rows=1)
    # 格式化为1x6向量: [x, y, z, dx, dy, dz]
    rv0 = rv0.reshape(1, -1)
    sat_num = len(rv0)

    # 计算轨道六根数
    oev0 = np.zeros((sat_num, 6))
    for i in range(sat_num):
        # 坐标转换为轨道六根数: [半长轴a, 偏心率e, 倾角i, 近地点幅角w, 升交点赤经Ω, 真近点角v]
        oev0[i, :] = PV_J2000_OEV(rv0[i, 0:3], rv0[i, 3:6])
    # 弧度转角度
    ove1 = np.rad2deg(oev0)
    print('oev0,', oev0)

    return rv0, oev0

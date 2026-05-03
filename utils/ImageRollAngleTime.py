import math
import numpy as np

from utils.LOS_YOZ_Angle import LOS_YOZ_Angle
from utils.geodetic_to_ecef import geodetic_to_ecef
from utils.OEV2PV_J2000 import OEV2PV_J2000
from utils.OrbitPropagation import OrbitPropagation
from utils.PV_J2000_OEV import PV_J2000_OEV
from utils.PV_J2000_WGS84 import PV_J2000_WGS84
from utils.P_WGS84_LLA import P_WGS84_LLA
from utils.haversine_distance import haversine_distance


def ImageRollAngleTime(jd, dt, r, v, lla):

    # 黄金分割法求过顶时刻
    k = 0.6180339887  # Golden ratio
    e = 1e-5  # Search time precision
    Re = 6371  # Earth radius in meters (assuming this was your Re)
    r2d = 180.0 / math.pi  # Radians to degrees conversion

    # 初始化值 (search start/end time)
    a = 0
    b = dt
    # b = 4000
    x1 = a + (1 - k) * (b - a)  # Left point
    x2 = a + k * (b - a)  # Right point

    oev = PV_J2000_OEV(r, v)

    # 求目标的地固坐标
    r_target = np.array(geodetic_to_ecef(lla[1] * r2d, lla[0] * r2d, 0)) / 1e3

    # 优化方式：0：在经纬度上求球面距离；  1：在地固坐标系中求欧氏距离  
    ### 几何学可以证明两者在结果上一致，而欧氏距离计算更快，可作为优化方式
    method = 0

    # f(x1) = dikma
    oev_a = OrbitPropagation(oev, x1)
    rija, vija = OEV2PV_J2000(oev_a)
    r_w84, _ = PV_J2000_WGS84(jd + x1 / 86400, rija, vija)
    if method == 0:
        llaa = P_WGS84_LLA(r_w84)[0]
        # dikma = haversine_distance(llaa[0] * r2d, llaa[1] * r2d, lon2, lat2, Re)
        dikma = haversine_distance(llaa[0], llaa[1], lla[0], lla[1], Re)
    elif method == 1:
        squared_diff = np.sum((r_target - np.array([r_w84[0], r_w84[1], r_w84[2]])) ** 2)
        dikma = np.sqrt(squared_diff)

    # f(x2) = dikmb
    oev_b = OrbitPropagation(oev, x2)
    rijb, vijb = OEV2PV_J2000(oev_b)
    r_w84, _ = PV_J2000_WGS84(jd + x2 / 86400, rijb, vijb)
    if method == 0:
        llab = P_WGS84_LLA(r_w84)[0]
        # dikmb = haversine_distance(llab[0] * r2d, llab[1] * r2d, lon2, lat2, Re)
        dikmb = haversine_distance(llab[0], llab[1], lla[0], lla[1], Re)
    elif method == 1:
        squared_diff = np.sum((r_target - np.array([r_w84[0], r_w84[1], r_w84[2]])) ** 2)
        dikmb = np.sqrt(squared_diff)

    point = []
    while abs(b - a) > e:
        # Iteratively solve for the minimum pitch angle point
        point.append([a, x1, x2, b, dikma, dikmb])
        if abs(dikma) < abs(dikmb):
            b = x2
            x2 = x1
            dikmb = dikma
            x1 = a + (1 - k) * (b - a)
            oev_a = OrbitPropagation(oev, x1)
            rija, vija = OEV2PV_J2000(oev_a)
            r_w84, _ = PV_J2000_WGS84(jd + x1 / 86400, rija, vija)

            if method == 0:
                llaa = P_WGS84_LLA(r_w84)[0]
                # dikma = haversine_distance(llaa[0] * r2d, llaa[1] * r2d, lon2, lat2, Re)
                dikma = haversine_distance(llaa[0], llaa[1], lla[0], lla[1], Re)
            elif method == 1:
                squared_diff = np.sum((r_target - np.array([r_w84[0], r_w84[1], r_w84[2]])) ** 2)
                dikma = np.sqrt(squared_diff)
        else:
            a = x1
            x1 = x2
            dikma = dikmb
            x2 = a + k * (b - a)
            oev_b = OrbitPropagation(oev, x2)
            rijb, vijb = OEV2PV_J2000(oev_b)
            r_w84, _ = PV_J2000_WGS84(jd + x2 / 86400, rijb, vijb)

            if method == 0:
                llab = P_WGS84_LLA(r_w84)[0]
                # dikmb = haversine_distance(llab[0] * r2d, llab[1] * r2d, lon2, lat2, Re)
                dikmb = haversine_distance(llab[0], llab[1], lla[0], lla[1], Re)
            elif method == 1:
                squared_diff = np.sum((r_target - np.array([r_w84[0], r_w84[1], r_w84[2]])) ** 2)
                dikmb = np.sqrt(squared_diff)

    image_time = (a + b) / 2


    # print(f'过顶时刻: {image_time}')


    # roll_angle, C = cal_roll(oev, image_time, lla[1] * 180 / math.pi, lla[0] * 180 / math.pi, 0)
    # roll_angle, _ = cal_roll(oev, image_time, lla[1] * 180 / math.pi, lla[0] * 180 / math.pi, 0)
    roll_angle = LOS_YOZ_Angle(oev, jd, image_time, lla[1] * 180 / math.pi, lla[0] * 180 / math.pi, 0)
    # 输出: 过顶时刻、滚转角、俯仰角
    return image_time, roll_angle / 180 * math.pi, 0

import numpy as np
from math import acos, degrees
from utils.PV_J2000_OEV import PV_J2000_OEV
from utils.OrbitPropagation import OrbitPropagation
from utils.OEV2PV_J2000 import OEV2PV_J2000
from utils.ImageAngle import ImageAngle
from utils.PV_J2000_WGS84 import PV_J2000_WGS84
from utils.P_WGS84_LLA import P_WGS84_LLA
from utils.haversine_distance import haversine_distance
from utils.geodetic_to_ecef import geodetic_to_ecef
from utils.ECEF2ECI import ECEF2ECI

# from PV_J2000_OEV import PV_J2000_OEV
# from OrbitPropagation import OrbitPropagation
# from OEV2PV_J2000 import OEV2PV_J2000
# from ImageAngle import ImageAngle
# from PV_J2000_WGS84 import PV_J2000_WGS84
# from P_WGS84_LLA import P_WGS84_LLA
# from haversine_distance import haversine_distance
# from geodetic_to_ecef import geodetic_to_ecef
# from ECEF2ECI import ECEF2ECI

def LOS_YOZ_Angle(oev, jd0, dt, lat, lon, alt):
    """
    计算卫星到目标点的视线在YOZ平面上的角度

    参数:
    oev: 轨道要素向量
    jd0: 初始儒略日
    dt: 时间差(秒)
    lat: 目标点纬度(度)
    lon: 目标点经度(度)
    alt: 目标点高度(米)

    返回:
    ang_1: 视线在YOZ平面上与+z轴的夹角(度)
    """
    # 计算该帧的JD(UTC)
    jd_img = jd0 + dt / 86400.0
    MJD_UTC_img = jd_img - 2400000.5

    # 1) 传播到指定时刻，得到 r,v（ECI->ECEF）
    oev_t = OrbitPropagation(oev, dt)
    r_eci, v_eci = OEV2PV_J2000(oev_t)

    # 2) 目标点 ECEF
    r_tgt_ecef = geodetic_to_ecef(lat, lon, alt)
    r_tgt_ecef = r_tgt_ecef.reshape(-1, 1)  # 转换为列向量
    Y0 = np.hstack((r_tgt_ecef.flatten(), [0, 0, 0]))  # 6x1 输入
    Y = ECEF2ECI(MJD_UTC_img, Y0) / 1000.0  # 转换到ECI坐标系并转换单位
    r_tgt_eci = Y[:3]  # 只取位置部分

    # 3) 视线向量处理

    # Body坐标系构造：x=速度方向；z=指地心；y右手补齐
    r_norm = np.linalg.norm(r_eci)
    rhat = r_eci / r_norm
    zB_I = -rhat  # +z_B 指天底

    v_norm = np.linalg.norm(v_eci)
    vhat = v_eci / v_norm

    # 去掉与 z 的分量（保证正交）
    vhat = vhat.flatten()  # 转为 (3,) 一维向量
    zB_I = zB_I.flatten()  # 转为 (3,) 一维向量
    x_tmp = vhat - np.dot(vhat, zB_I) * zB_I
    xB_I = x_tmp / np.linalg.norm(x_tmp)

    # 右手定则确定y轴
    yB_I = np.cross(zB_I, xB_I)
    yB_I = yB_I / np.linalg.norm(yB_I)

    # ECI -> Body 的 被动旋转矩阵（行向量=Body轴在ECI下的坐标）
    C_BI = np.vstack((xB_I, yB_I, zB_I))

    # LOS：卫星→目标，并变到 Body 坐标系
    r_eci = r_eci.flatten()
    los_eci = r_tgt_eci - r_eci
    los_eci = los_eci / np.linalg.norm(los_eci)
    los_B = np.dot(C_BI, los_eci)

    # 在 YOZ 面投影 与 +z_B 的夹角（0..pi）
    py = los_B[1]
    pz = los_B[2]

    # 计算角度
    theta = np.arctan2(py, pz)
    ang_1 = np.rad2deg(theta)

    return ang_1


import numpy as np
from utils.OrbitPropagation import OrbitPropagation
from utils.OEV2PV_J2000 import OEV2PV_J2000
from utils.PV_J2000_WGS84 import PV_J2000_WGS84
from utils.P_WGS84_LLA import P_WGS84_LLA


def track_point(jd0, oev0, dt, step):
    len = int(dt / step) + 1  # 步长
    lla = np.zeros((len, 3))
    for i in range(oev0.shape[0]):
        for j in range(len):
            t = j * step
            # 轨道传播
            oev_ij = OrbitPropagation(oev0[i, :], t)
            # 将轨道要素转换为位置和速度
            rij, vij = OEV2PV_J2000(oev_ij)
            # 将 J2000 坐标系下的位置和速度转换为 WGS84 坐标系
            r_w84, _ = PV_J2000_WGS84(jd0 + t / 86400, rij, vij)
            # 将 WGS84 坐标系下的位置转换为经纬度
            lla[j, :] = P_WGS84_LLA(r_w84)
    return lla

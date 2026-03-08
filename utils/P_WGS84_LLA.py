import numpy as np


def P_WGS84_LLA(r_WGS84):
    # WGS84坐标系位置转大地坐标系经纬高
    # 输入：
    #  WGS84坐标系位置 r_WGS84(3)    (km)
    # 输出：
    #  经纬高 lla(3)
    #  lla[0] = longitude       经度    (rad)
    #  lla[1] = latitude  纬度          (rad)
    #  lla[2] = altitude     高度       (km)

    # 地球扁率平方
    e_Earth = 0.08181921805
    e_Earth2 = e_Earth ** 2

    # 地球半径
    r_Earth = 6378.137

    # 迭代次数
    N = 10

    rx = r_WGS84[0]
    ry = r_WGS84[1]
    rz = r_WGS84[2]

    if ry >= 0:
        lon = np.arccos(rx / np.sqrt(rx * rx + ry * ry))
    else:
        lon = -np.arccos(rx / np.sqrt(rx * rx + ry * ry))

    lat = np.arctan(rz / np.sqrt(rx * rx + ry * ry))

    for i in range(N):
        r = r_Earth / np.sqrt(1 - e_Earth2 * np.sin(lat) * np.sin(lat))
        lat = np.arctan((rz + e_Earth2 * r * np.sin(lat)) / np.sqrt(rx * rx + ry * ry))

    alt = rx / np.cos(lon) / np.cos(lat) - r
    lla = np.array([lon, lat, alt])

    return lla.T

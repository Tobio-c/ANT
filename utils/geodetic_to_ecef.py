import numpy as np


def geodetic_to_ecef(lat, lon, alt):
    """
    将地理坐标（纬度、经度、高度）转换为地心地固坐标系（ECEF）

    参数:
    lat, lon: 纬度和经度，单位为度
    alt: 高度，单位为米

    返回:
    r_ecef: 地心地固坐标系下的三维位置向量 [x, y, z]
    """

    # WGS84参数
    a = 6378137.0  # 长半轴 (米)
    f = 1 / 298.257223563  # 扁率
    e2 = 2 * f - f ** 2  # 偏心率的平方

    # 角度转换为弧度
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)

    # 计算曲率半径
    sin_lat = np.sin(lat_rad)
    N = a / np.sqrt(1 - e2 * sin_lat ** 2)

    # 计算ECEF坐标
    cos_lat = np.cos(lat_rad)
    cos_lon = np.cos(lon_rad)
    sin_lon = np.sin(lon_rad)

    x = (N + alt) * cos_lat * cos_lon
    y = (N + alt) * cos_lat * sin_lon
    z = (N * (1 - e2) + alt) * sin_lat

    return np.array([x, y, z])


if __name__ == '__main__':
    print(geodetic_to_ecef(39.4492, 121.644, 0))
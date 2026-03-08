import numpy as np


def haversine_distance(lon1, lat1, lon2, lat2, r):
    """
    计算两个经纬度点之间的距离
    :param lon1: 第一个点的经度
    :param lat1: 第一个点的纬度
    :param lon2: 第二个点的经度
    :param lat2: 第二个点的纬度
    :param R: 地球半径
    :return: 两点之间的距离
    """
    #lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])  # 角度转弧度
    delta_lon = lon2 - lon1
    delta_lat = lat2 - lat1
    a = np.sin(delta_lat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(delta_lon / 2) ** 2
    # c = 2 * np.arcsin(np.sqrt(a))
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return r * c

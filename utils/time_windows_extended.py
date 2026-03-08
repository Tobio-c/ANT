import numpy as np
from utils.haversine_distance import haversine_distance


def time_windows_extended(sat_lla, radius_earth, lon, lat):
    FOV = 45  # 相机视场角 (°)

    # 初始化变量
    visible = False
    time_windows = []
    start_time = np.nan  # 开始时间
    for i in range(len(sat_lla)):
        # 计算当前时刻的成像半径
        r = sat_lla[i, 2] * np.tan(np.deg2rad(FOV))

        # 计算当前时刻卫星与目标的距离
        distance = haversine_distance(sat_lla[i, 0], sat_lla[i, 1],
                                      lon, lat, radius_earth)
        # print(distance)

        # 判断是否在观测范围内
        if distance < r:
            if not visible:
                # 如果刚进入观测范围，记录开始时间
                start_time = i - 1
                visible = True
        else:
            if visible:
                # 如果刚离开观测范围，记录结束时间
                end_time = i - 1
                time_windows.append([start_time, end_time])  # 添加时间窗口
                visible = False

        # 如果没有任何时间窗口，则返回空数组
    if not time_windows:
        time_windows = []
    return np.array(time_windows)

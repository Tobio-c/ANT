import numpy as np
from datetime import timedelta
from utils.time_windows_extended import time_windows_extended
from utils.track_point import track_point


def cal_time_windows(current_time, jd0, oev0, lon, lat):
    radius_earth = 6371  # 地球半径 (km)
    step = 1  # 轨道预报间隔 (s)
    dt = 86400  # 轨道预报的总时长(s) 1天: 86400s   6h
    num_i = len(lon)  # 目标点个数
    # 生成卫星星下点轨迹
    sat_lla = track_point(jd0, oev0, dt, step)  # (rad)
    print("星下点轨迹sat_lla: ", sat_lla)

    # 存储所有目标点的时间窗口（字典）
    allTarget_time_windows = {i: [] for i in range(1, num_i+1)}
    print(allTarget_time_windows)

    # 循环依此计算每个目标点i的时间窗口
    for i, key in enumerate(allTarget_time_windows):

        # 生成目标点i所有时间窗口的长度
        windows_len = time_windows_extended(sat_lla, radius_earth, lon[i], lat[i])

        # 计算可见时间窗口
        for window_len in windows_len:
            allTarget_time_windows[key].append([current_time + timedelta(seconds=int(window_len[0])), current_time + timedelta(seconds=int(window_len[1]))])



    # 打印每个目标点i的时间窗口
    # for i, time_window in enumerate(all_time_windows):
    #     print(f'目标点{i+1}时间窗口为:', time_window)
    return allTarget_time_windows

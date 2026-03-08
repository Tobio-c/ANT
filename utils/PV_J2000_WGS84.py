import numpy as np


def PV_J2000_WGS84(jd, r_J2000, v_J2000):
    # J2000坐标系位置速度转WGS84坐标系位置速度
    # 输入：
    #  儒略日            jd            (days)
    #  J2000坐标系位置   r_J2000(3)    (km)
    #  J2000坐标系速度   v_J2000(3)    (km/s)
    # 输出：
    #  WGS84坐标系位置   r_WGS84(3)    (km)
    #  WGS84坐标系速度   v_WGS84(3)    (km/s)

    T = (jd - 2451545) / 36525  # 儒略世纪数
    zeta = 0.011180860 * T + 1.464 * (10 ** (-6)) * (T ** 2) + 8.7 * (10 ** (-8)) * (T ** 3)
    z = 0.011180860 * T + 5.308 * (10 ** (-6)) * (T ** 2) + 8.9 * (10 ** (-8)) * (T ** 3)
    theta = 0.009717173 * T - 2.068 * (10 ** (-6)) * (T ** 2) - 2.02 * (10 ** (-7)) * (T ** 3)

    R11 = np.array([[np.cos(-zeta), np.sin(-zeta), 0],
                    [-np.sin(-zeta), np.cos(-zeta), 0],
                    [0, 0, 1]])

    R12 = np.array([[np.cos(theta), 0, -np.sin(theta)],
                    [0, 1, 0],
                    [np.sin(theta), 0, np.cos(theta)]])

    R13 = np.array([[np.cos(-z), np.sin(-z), 0],
                    [-np.sin(-z), np.cos(-z), 0],
                    [0, 0, 1]])

    P = np.matmul(np.matmul(R13, R12), R11)

    thast = 67310.54841 + (876600 * 3600 + 8640184.812866) * T + 0.0093104 * T ** 2 - 6.2 * 10 ** (-6) * T ** 3
    thast = thast % 86400
    thast = thast / 240
    thast = thast / 180 * np.pi
    R = np.array([[np.cos(thast), np.sin(thast), 0],
                  [-np.sin(thast), np.cos(thast), 0],
                  [0, 0, 1]])

    W = np.matmul(R, P)

    r_WGS84 = np.matmul(W, r_J2000)

    omega_Earth = np.array([0, 0, -7.292123516990375e-5])
    add = np.cross(omega_Earth.flatten(), r_J2000.flatten()).reshape((3, 1))
    #add = np.cross(omega_Earth, r_J2000)
    v_WGS84 = np.matmul(W, v_J2000 + add)

    return r_WGS84, v_WGS84

import numpy as np

def LLA2P_WGS84(lla):
    e_Earth = 0.08181921805
    e_Earth2 = e_Earth**2

    r_Earth = 6378.137

    v = r_Earth / np.sqrt(1 - e_Earth2 * np.sin(lla[1]) * np.sin(lla[1]))
    r_WGS84 = np.zeros((3, 1))
    r_WGS84[0, 0] = (v + lla[2]) * np.cos(lla[1]) * np.cos(lla[0])
    r_WGS84[1, 0] = (v + lla[2]) * np.cos(lla[1]) * np.sin(lla[0])
    r_WGS84[2, 0] = ((1 - e_Earth2) * v + lla[2]) * np.sin(lla[1])

    return r_WGS84

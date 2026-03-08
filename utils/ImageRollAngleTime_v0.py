import numpy as np
from utils.PV_J2000_OEV import PV_J2000_OEV
from utils.OrbitPropagation import OrbitPropagation
from utils.OEV2PV_J2000 import OEV2PV_J2000
from utils.ImageAngle import ImageAngle
def ImageRollAngleTime(jd, dt, r, v, lla):
    # 牛顿迭代法
    e = 1e-3
    i = 0
    N = 10

    x0 = 0
    x1 = dt / 2
    if dt == 0:
        x1 = 2 * e
    v1 = np.pi / 2

    oev = PV_J2000_OEV(r, v)

    while (abs(x1 - x0) > e) and (abs(v1) > e) and (i < N):
        x0 = x1
        if x0 < 0:
            x0 = 0
        elif x0 > dt:
            x0 = dt
        oev0 = OrbitPropagation(oev, x0)
        r0, v0 = OEV2PV_J2000(oev0)
        roll0, pitch0 = ImageAngle(jd + x0 / 86400, r0, v0, lla)
        xd = x0 + e
        oevd = OrbitPropagation(oev, xd)
        rd, vd = OEV2PV_J2000(oevd)
        _, pitchd = ImageAngle(jd + xd / 86400, rd, vd, lla)
        v1 = pitch0
        v2 = (pitchd - pitch0) / e
        x1 = x0 - v1 / v2
        i = i + 1

    roll_angle = roll0
    image_time = x0
    C = pitch0
    # 输出限幅
    if (i == N) or (image_time <= 1) or (image_time >= dt - 1):
        image_time = 0
        roll_angle = 0
    # 输出: 过顶时刻、滚转角、俯仰角
    return image_time, roll_angle, C
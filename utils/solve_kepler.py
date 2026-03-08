import math


def solve_kepler(e, M0):
    e1 = -1
    e2 = 1e-9
    e3 = 1e-6
    k1 = 1
    N = 50

    if M0 > 2 * math.pi:
        M0 = M0 % (2 * math.pi)

    x0 = M0
    v1 = x0 - e * math.sin(x0) - M0
    v2 = 1 - e * math.cos(x0)

    # 迭代求解 x1
    if abs(v1) >= e1 and abs(v2) >= e1:
        x1 = x0 - v1 / v2
        while abs(x1 - x0) > e2 and abs(v1) > e3 and k1 < N:
            k1 += 1
            x0 = x1
            v1 = x0 - e * math.sin(x0) - M0
            v2 = 1 - e * math.cos(x0)
            x1 = x0 - v1 / v2
        if k1 > N:
            x1 = -1  # 无解
    else:
        x1 = -1
    E0 = x1
    return E0

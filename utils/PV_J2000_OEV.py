import numpy as np


def PV_J2000_OEV(r, v):
    # Converts ECI state vector to six classical orbital elements via equinoctial elements

    # input
    # r: eci position vector (km)
    # v: eci velocity vector (km/sec)

    # output
    # oev[0]: semimajor axis (km)
    # oev[1]: orbital eccentricity (-)
    # oev[2]: orbital inclination (rad)
    # oev[3]: argument of perigee (rad)
    # oev[4]: right ascension of ascending node (rad)
    # oev[5]: true anomaly (rad)

    # Position and velocity magnitude
    rmag = np.sqrt(np.dot(r, r))
    vmag = np.sqrt(np.dot(v, v))

    # Position and velocity unit vectors
    rhat = r / rmag

    # Angular momentum vectors
    hv = np.cross(r, v)
    hhat = hv / np.linalg.norm(hv)
    mu = 398600.4415  # Earth Gravitational Constant, [km^3/sec^2]
    # Eccentricity vector
    vtmp = v / mu
    ecc = np.cross(vtmp, hv)
    ecc = ecc - rhat

    # Semimajor axis
    sma = 1 / (2 / rmag - vmag * vmag / mu)

    p = hhat[0] / (1 + hhat[2])
    q = -hhat[1] / (1 + hhat[2])
    if hhat[0] == 0:
        p = 0
    if hhat[1] == 0:
        q = 0
    const1 = 1 / (1 + p * p + q * q)
    fhat = np.zeros(3)
    fhat[0] = const1 * (1 - p * p + q * q)
    fhat[1] = const1 * 2 * p * q
    fhat[2] = -const1 * 2 * p
    ghat = np.zeros(3)
    ghat[0] = const1 * 2 * p * q
    ghat[1] = const1 * (1 + p * p - q * q)
    ghat[2] = const1 * 2 * q
    h = np.dot(ecc, ghat)
    xk = np.dot(ecc, fhat)
    x1 = np.dot(r, fhat)
    y1 = np.dot(r, ghat)

    # Orbital eccentricity
    eccm = np.sqrt(h * h + xk * xk)

    # Orbital inclination
    inc = 2 * np.arctan(np.sqrt(p * p + q * q))

    # True longitude
    xlambdat = np.arctan2(y1, x1)

    # Check for equatorial orbit
    if inc > 0.00000001:
        raan = np.mod(np.arctan2(p, q), 2 * np.pi)
    else:
        raan = 0

    # Check for circular orbit
    if eccm > 0.00000001:
        argper = np.mod(np.mod(np.arctan2(h, xk), 2 * np.pi) - raan, 2 * np.pi)
    else:
        argper = 0

    # True anomaly
    tanom = np.mod(xlambdat - raan - argper, 2 * np.pi)
    if hhat[2] == -1:
        tanom = np.mod(xlambdat - raan - argper, 2 * np.pi)

    # Singular value when hhat[2] == -1
    if hhat[2] == -1:
        inc = np.pi
        raan = np.pi
        argper = np.mod(-np.arctan2(h, xk) + raan, 2 * np.pi)
        tanom = np.mod(xlambdat - raan - argper, 2 * np.pi)

    # Orbital element vector
    oev = np.array([sma, eccm, inc, argper, raan, tanom])
    return oev

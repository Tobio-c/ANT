import math
import numpy as np
def OEV2PV_J2000(oev):
    sma = oev[0]
    ecc = oev[1]
    inc = oev[2]
    argper = oev[3]
    raan = oev[4]
    tanom = oev[5]
    mu = 398600.4415
    slr = sma * (1 - ecc * ecc)
    rm = slr / (1 + ecc * math.cos(tanom))

    arglat = argper + tanom
    sarglat = math.sin(arglat)
    carglat = math.cos(arglat)

    c4 = math.sqrt(mu / slr)
    c5 = ecc * math.cos(argper) + carglat
    c6 = ecc * math.sin(argper) + sarglat

    sinc = math.sin(inc)
    cinc = math.cos(inc)
    sraan = math.sin(raan)
    craan = math.cos(raan)

    r_J2000 = np.zeros((3, 1))

    r_J2000[0, 0] = rm * (craan * carglat - sraan * sarglat * cinc)
    r_J2000[1, 0] = rm * (sraan * carglat + craan * sarglat * cinc)
    r_J2000[2, 0] = rm * sarglat * sinc



    v_J2000 = np.zeros((3, 1))
    v_J2000[0, 0] = -c4 * (c6 * craan + c5 * sraan * cinc)
    v_J2000[1, 0] = -c4 * (c6 * sraan - c5 * craan * cinc)
    v_J2000[2, 0] = c4 * c5 * sinc
    return r_J2000, v_J2000



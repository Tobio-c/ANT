import numpy as np
def JulianDay(yr, mon, day, hr, minute, sec):
    # this function finds the julian date given the year, month, day, and time.
    # author: david vallado (27 may 2002)

    # inputs:
    # yr: year (1900 .. 2100)
    # mon: month (1 .. 12)
    # day: day (1 .. 28,29,30,31)
    # hr: universal time hour (0 .. 23)
    # minute: universal time min (0 .. 59)
    # sec: universal time sec (0.0 .. 59.999)

    # outputs:
    # jd: julian date (days from 4713 bc)

    jd = 367.0 * yr \
         - np.floor((7 * (yr + np.floor((mon + 9) / 12.0))) * 0.25) \
         + np.floor(275 * mon / 9.0) \
         + day + 1721013.5 \
         + (((sec / 60.0 + minute) / 60.0) + hr) / 24.0
    return jd
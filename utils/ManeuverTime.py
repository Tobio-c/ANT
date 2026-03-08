import math
import numpy as np
def ManeuverTime(angle1, angle2):
    delta_angle = abs(angle1 - angle2) * 180 / math.pi

    # if delta_angle <= 20:
    if np.all(delta_angle <= 20):

        # dt = math.sqrt(delta_angle * 5) + 10
        dt = np.sqrt(delta_angle * 5) + 10

    else:
        dt = delta_angle / 2 + 10

    return dt

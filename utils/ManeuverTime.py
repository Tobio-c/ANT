import math
import numpy as np
def ManeuverTime(angle1, angle2):
    delta_angle = abs(angle1 - angle2) * 180 / math.pi

### +10可能是固定的准备时间或最小机动时间
    # if delta_angle <= 20:
    if np.all(delta_angle <= 20):

        # dt = math.sqrt(delta_angle * 5) + 10
        dt = np.sqrt(delta_angle * 5) + 10  ### 小角度机动时，机动时间与角度差的平方根成正比

    else:
        dt = delta_angle / 2 + 10      ### 大角度机动时，机动时间与角度差成线性关系

    return dt

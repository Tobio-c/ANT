from utils.ManeuverTime import ManeuverTime
import numpy as np
# def NextProfit(tar1, tar2, tar_cal):
#     alpha = 1
#     beta = 0.05
#     gamma = 0.002
#     image_dt = 0
#     tar1 = int(tar1)
#     tar2 = int(tar2)
#     # tar2 = tar2.astype(int)
#
#
#     if tar1 == 0:
#         profit = alpha - beta * abs(tar_cal[tar2 - 1, 6]) - gamma * abs(tar_cal[tar2 - 1, 5])
#
#
#
#     # elif tar_cal[tar2 - 1, 4] == 0:
#     elif np.any(tar_cal[tar2 - 1, 4] == 0):
#         profit = gamma * tar_cal[tar2 - 1, 5] / 100
#         s = tar_cal[tar2 - 1, 5]
#     else:
#         maneuver_dt = ManeuverTime(tar_cal[tar1 - 1, 6], tar_cal[tar2 - 1, 6])
#         # if maneuver_dt + image_dt > tar_cal[tar2 - 1, 5] - tar_cal[tar1 - 1, 5]:
#         if np.all(maneuver_dt + image_dt > tar_cal[tar2 - 1, 5] - tar_cal[tar1 - 1, 5]):
#             profit = 0
#         else:
#             profit = alpha - beta * abs(tar_cal[tar2 - 1, 6] - tar_cal[tar1 - 1, 6]) - gamma * abs(
#                 tar_cal[tar2 - 1, 5] - tar_cal[tar1 - 1, 5])
#
#     return profit

###考虑天气收益
# def NextProfit(tar1, tar2, tar_cal):
#     # 计算下次观测目标收益
#     # 收益指标: 成像收益 - 机动消耗 - 总时间增量
#     # 收益指标：权重
#     alpha = 1
#     beta = 0.05
#     gamma = 0.002
#     image_dt = 0
#     # s = tar_cal[tar2 - 1, 4]
#     a = tar_cal[int(tar2 - 1), 4]
#     if tar1 == 0:
#         if tar_cal[int(tar2 - 1), 4] == 1:
#             profit = 1
#         else:
#             profit = alpha - beta * abs(tar_cal[int(tar2 - 1), 6]) - gamma * abs(tar_cal[int(tar2 - 1), 5])
#         # profit = tar_cal[tar2, 4]
#     elif tar_cal[int(tar2 - 1), 4] == 0:
#         # profit = gamma * tar_cal[tar2 - 1, 5] / 100
#         profit = 0
#     else:
#         maneuver_dt = ManeuverTime(tar_cal[int(tar1 - 1), 6], tar_cal[int(tar2 - 1), 6])  # 机动时间  滚转角rad
#         if maneuver_dt + image_dt > tar_cal[int(tar2 - 1), 5] - tar_cal[int(tar1 - 1), 5]:  # 机动时间+成像时间 > 两目标点的过顶时刻
#             profit = 0
#         else:
#             if tar_cal[int(tar2 - 1), 4] == 1:
#                 profit = 1
#             else:
#                 profit = alpha - beta * abs(tar_cal[int(tar2 - 1), 6] - tar_cal[int(tar1 - 1), 6]) - gamma * abs(
#                     tar_cal[int(tar2 - 1), 5] - tar_cal[int(tar1 - 1), 5])
#             # profit = tar_cal[tar2, 4]
#     return profit
# 不考虑天气收益
def NextProfit(tar1, tar2, tar_cal):
    # 计算下次观测目标收益
    # 收益指标: 成像收益 - 机动消耗 - 总时间增量
    # 收益指标：权重
    alpha = 2
    beta = 0.05
    gamma = 0.002
    image_dt = 0
    # s = tar_cal[tar2 - 1, 4]
    a = tar_cal[int(tar2 - 1), 4]
    if tar1 == 0:
        profit = alpha - beta * abs(tar_cal[int(tar2 - 1), 6]) - gamma * abs(tar_cal[int(tar2 - 1), 5])
        # profit = tar_cal[tar2, 4]
    elif tar_cal[int(tar2 - 1), 4] == 0:
        profit = gamma * tar_cal[tar2 - 1, 5] / 100

    else:
        maneuver_dt = ManeuverTime(tar_cal[int(tar1 - 1), 6], tar_cal[int(tar2 - 1), 6])  # 机动时间  滚转角rad
        if maneuver_dt + image_dt > tar_cal[int(tar2 - 1), 5] - tar_cal[int(tar1 - 1), 5]:  #
            profit = 0
        else:
            profit = alpha - beta * abs(tar_cal[int(tar2 - 1), 6] - tar_cal[int(tar1 - 1), 6]) - gamma * abs(
                tar_cal[int(tar2 - 1), 5] - tar_cal[int(tar1 - 1), 5])
            # profit = tar_cal[tar2, 4]
    return profit



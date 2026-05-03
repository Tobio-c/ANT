from utils.ManeuverTime import ManeuverTime
import numpy as np

# 成像物理与能耗参数（你可以根据实际卫星调整）
T_EXP_MIN = 5.0    # 最短有效曝光时间(秒)
DELTA = 0.3        # 曝光时间对收益的对数敏感度系数
ETA = 0.01         # 每秒开机成像的能耗惩罚权重

def optimal_exposure(available_time, importance):
    """
    通过对数收益与线性惩罚求导，计算真实的经济最优曝光时间
    理论极值点: t_opt = (importance * DELTA) / ETA
    """
    t_opt = (importance * DELTA) / ETA
    # 结合真实物理环境约束进行截断
    t_exp = min(t_opt, available_time)               # 在理论最优和可用时间中取小值
    t_exp = max(t_exp, T_EXP_MIN)                # 兜底：不能低于最短有效开机时间
    
    return t_exp


def image_quality_gain(importance, t_exp):
    """成像质量收益：重要程度 × 曝光时间对数饱和增益"""
    return importance * (0.5 + DELTA * np.log(t_exp / T_EXP_MIN))



def NextProfit(tar1, tar2, tar_cal):
    # 收益指标: 成像质量增益 - 机动能耗惩罚 - 等待时间惩罚 - 成像耗电惩罚
    beta = 0.05      ## 机动惩罚系数
    gamma = 0.002    ## 时间惩罚系数
    
    importance2 = 3 * tar_cal[int(tar2 - 1), 4]  ## 基础收益为目标的重要程度得分

    if tar1 == 0:  ### 情况1：从零开始新观测
        # 初始状态时间无限(传入无穷大)，但依然要受限于经济最优解 t_opt
        t_exp = optimal_exposure(float('inf'), importance2)
        alpha = image_quality_gain(importance2, t_exp)
        
        profit = alpha - beta * abs(tar_cal[int(tar2 - 1), 6]) \
                       - gamma * abs(tar_cal[int(tar2 - 1), 5]) \
                       - ETA * t_exp
                       
    elif importance2 == 0:  ### 情况2：目标不可观测
        profit = gamma * tar_cal[int(tar2 - 1), 5] / 100
        
    else:  ### 情况3：正常目标间的动态转移
        maneuver_dt = ManeuverTime(tar_cal[int(tar1 - 1), 6], tar_cal[int(tar2 - 1), 6])
        time_gap = tar_cal[int(tar2 - 1), 5] - tar_cal[int(tar1 - 1), 5]
        available_time = time_gap - maneuver_dt  
        
        if available_time < T_EXP_MIN:  
            profit = 0
        else:
            # 动态计算该目标在当前环境下的真实最优曝光时间
            t_exp = optimal_exposure(available_time, importance2)
            alpha = image_quality_gain(importance2, t_exp)
            
            profit = alpha - beta * abs(tar_cal[int(tar2 - 1), 6] - tar_cal[int(tar1 - 1), 6]) \
                           - gamma * abs(time_gap) \
                           - ETA * t_exp

    return profit
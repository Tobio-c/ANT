import numpy as np
from utils.ImageRollAngleTime import ImageRollAngleTime
from utils.NextProfit import NextProfit
from utils.OrderProfit import OrderProfit
from utils.PV_J2000_OEV import PV_J2000_OEV
from utils.cal_time_windows import cal_time_windows


def mission_planning_aco(oev, current_time, jd, dt, r, v, target_lib):
    '''Mission_planning_aco函数
    输入: ( 初始时间jd0, 时间步长dt 秒,  卫星初始状态的轨道位置(x,y,z), 卫星初始状态的轨道速度(dx,dy,dz), 目标点序列)
    '''
    # 预处理
    tar_len = len(target_lib)
    # tar_info -- [序号, 经度, 维度, 高度, 重要程度, 过顶时刻, 滚转角, 俯仰角]
    tar_info = np.zeros((tar_len, 9))
    tar_info[:, :5] = target_lib
    for i in range(tar_len):
        '''
        输入: key_target_lib[i, 2:5], 第i个目标点的经度、纬度、高度
        输出: 过顶时刻、滚转角、俯仰角
        '''
        tar_info[i, 5], tar_info[i, 6], tar_info[i, 7] = ImageRollAngleTime(jd, dt, r, v, target_lib[i, 1:4])

    '''
    cal_time_windows: 计算每个目标点的可见窗口
    输入: (初始时间jd, 轨道六根数oev0(rad), 目标点经度, 目标点纬度)
    '''
    allTarget_time_windows = cal_time_windows(current_time, jd, oev, tar_info[:, 1], tar_info[:, 2])

    # 参数设置
    m = 10  # 蚂蚁的数量
    n = tar_len  # 任务的数量
    alpha = 1  # 信息素
    beta = 5  # 启发式信息的权重
    vol = 0.1  # 信息素挥发率
    q = 0.1  # 信息素增加系数
    tau = np.ones((n, n))  # 信息素矩阵，初始值全为1
    table = np.zeros((m,n))  # 蚂蚁的路径表，记录每只蚂蚁选择的任务序列
    iter_max = 10  # 最大迭代次数
    profit = np.zeros(m)  # 每只蚂蚁的任务序列的总收益
    order_best = np.zeros((iter_max, n))  # 每次迭代的最优任务序列
    profit_best = np.zeros(iter_max)  # 每次迭代的最优收益
    profit_ave = np.zeros(iter_max)  # 每次迭代的平均收益
    iter_limit = 0  # 记录达到最优解的迭代次数

    # 控制迭代次数
    for iteration in range(iter_max):
        # 构建解空间
        tar_index = np.arange(1, n + 1)   #### 已更正
        # 每只蚂蚁依次选择任务
        for i in range(m):
            for j in range(n):
                tabu = table[i, :j]  # 禁忌表，记录已经选择的任务
                allow_index = ~np.isin(tar_index, tabu)
                allow = tar_index[allow_index]  # 可用任务列表，即未被选择的任务
                tabu = tabu.astype(int)
                allow = allow.astype(int)
                p = np.copy(allow).astype(float)  # 选择每个可用任务的概率
                for k in range(len(allow)):
                    if len(tabu) == 0:
                        heu_value = NextProfit(0, allow[k], tar_info)  # 启发式信息，通过NextProfit函数计算
                        p[k] = heu_value ** beta
                    else:
                        heu_value = NextProfit(tabu[-1], allow[k], tar_info)
                        p[k] = tau[int(tabu[-1]) - 1, int(allow[k]) - 1] ** alpha * heu_value ** beta
                if np.sum(p) == 0:
                    break
                else:
                    p = p / np.sum(p)
                pc = np.cumsum(p)
                target_index = np.where(pc >= np.random.rand())[0]
                target = allow[target_index[0]]  # 根据概率选择的下一个任务
                table[i, j] = target

            profit[i] = OrderProfit(table[i], tar_info)  # 第i只蚂蚁的任务序列的总收益，通过OrderProfit函数计算

        # 计算最佳收益及平均收益
        if iteration == 0:
            profit_max, index_max = np.max(profit), np.argmax(profit)
            profit_best[iteration] = profit_max  # profit_best 记录每次迭代的最优收益
            profit_ave[iteration] = np.mean(profit)  # profit_ave 记录每次迭代的平均收益
            order_best[iteration] = table[index_max]  # order_best 记录每次迭代的最优任务序列
            iter_limit = 1  # iter_limit 记录达到最优解的迭代次数
        else:
            profit_max, index_max = np.max(profit), np.argmax(profit)
            profit_best[iteration] = max(profit_best[iteration - 1], profit_max)
            profit_ave[iteration] = np.mean(profit)
            if profit_best[iteration] == profit_max:
                order_best[iteration] = table[index_max]
                iter_limit = iteration + 1
            else:
                order_best[iteration] = order_best[iteration - 1]

        # 更新信息素
        delta_tau = np.zeros((n, n))  # delta_tau：信息素增量矩阵，记录每只蚂蚁对信息素的贡献
        for i in range(m):
            for j in range(n - 1):
                if table[i, j + 1] == 0:
                    break
                table = table.astype(int)
                delta_tau[table[i, j] - 1, table[i, j + 1] - 1] += q * profit[i]
        tau = (1 - vol) * tau + delta_tau  # tau：信息素矩阵，根据信息素挥发率和增量进行更新
        table = np.zeros((m, n))  # table：清空路径表，为下一次迭代做准备

    task_profit, index = np.max(profit_best), np.argmax(profit_best)
    task = order_best[index]

    print(f"选择的原始task是: {task}")

    # 如果task里有0，才进行切片
    if 0 in task:
        first_zero_index = np.where(task == 0)[0][0]
        # --- 在这里加入调试打印 ---
        print(f"第一个0的索引是: {first_zero_index}")
        # -------------------------
        task = task[:first_zero_index]
    else:
        # 如果没有0，可以根据你的业务逻辑决定如何处理，这里我们先打印一下
        print("警告：task中没有0，无法进行切片。")

    # --- 在这里加入调试打印 ---
    print(f"切片后的task是: {task}")

    #task = task[:np.where(task == 0)[0][0]]
    task = task.astype(int)
    task = sorted(task)
    task = np.array(task)

    C = tar_info  # [序号, 经度, 维度, 高度, 重要程度, 过顶时刻, 滚转角, 俯仰角, 时间窗口]
    print("任务规划迭代次数:\n", iter_limit)
    # task_profit: 最大收益， task: 最佳任务序列，排序并去除末尾的 0， C: 任务计算信息  time_windows: 时间窗口
    return task, task_profit, C, allTarget_time_windows
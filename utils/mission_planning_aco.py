import numpy as np
from utils.ImageRollAngleTime import ImageRollAngleTime
from utils.NextProfit import NextProfit
from utils.OrderProfit import OrderProfit
from utils.PV_J2000_OEV import PV_J2000_OEV
from utils.cal_time_windows import cal_time_windows
from utils.objective_metrics import evaluate_order, evaluate_transition, preference_heuristic
from utils.pareto import update_archive, get_pareto_front
np.random.seed(42)  # 设置固定种子

def mission_planning_aco(
    oev,
    current_time,
    jd,
    dt,
    r,
    v,
    target_lib,
    return_pareto=False,
    archive_max_size=100,
    ):
    '''Mission_planning_aco函数
    输入: ( 初始时间jd0, 时间步长dt 秒,  卫星初始状态的轨道位置(x,y,z), 卫星初始状态的轨道速度(dx,dy,dz), 目标点序列)
    app.py中mission_planning_aco(oev0, current_time, jd0, dt, rv0[0, 0:3], rv0[0, 3:6], key_target_lib)
    '''
    # 预处理
    tar_len = len(target_lib)   ## tar_len = 107
    # tar_info -- [序号, 经度, 维度, 高度, 重要程度, 过顶时刻, 滚转角, 俯仰角,时间窗口]
    tar_info = np.zeros((tar_len, 9))
    tar_info[:, :5] = target_lib
    for i in range(tar_len):
        '''
        输入: key_target_lib[i, 2:5], 第i个目标点的经度、纬度、高度
        输出: 过顶时刻//[、滚转角、俯仰角]
        '''###这里的dt为app.py传入的值
        tar_info[i, 5], tar_info[i, 6], tar_info[i, 7] = ImageRollAngleTime(jd, dt, r, v, target_lib[i, 1:4])



    '''
    cal_time_windows: 计算每个目标点的可见窗口
    输入: (初始时间jd, 轨道六根数oev0(rad), 目标点经度, 目标点纬度)
    '''
    # allTarget_time_windows = cal_time_windows(current_time, jd, oev, tar_info[:, 1], tar_info[:, 2])
    ###暂时取消对时间窗口的计算
    allTarget_time_windows = {}


    # ===  调试打印    ===
    ### 测试tar_info数据内容
    # print("tar_info 前5行数据：")
    # print("tar_info -- [序号, 经度, 维度, 高度, 重要程度, 过顶时刻, 滚转角, 俯仰角,时间窗口]")
    # print(tar_info[:5])  # 打印前5行所有列
    # ===  调试打印    ===



    # 参数设置
    m = 150       # 蚂蚁的数量
    n = tar_len  # 任务的数量 ###0703中为107个
    alpha = 1    # 信息素
    beta = 1   # 启发式信息（NextProfit）的权重
    vol = 0.05    # 信息素挥发率
    q = 0.2      # 信息素增加系数
    tau_min = 0.1
    tau_max = 4.0

    
    preference_names = ["value_first", "energy_first", "balanced"] # 三套信息素矩阵。
    tau_by_preference = {
        name: np.ones((n, n)) for name in preference_names
    }


    table = np.zeros((m,n))  # 蚂蚁的路径表，记录每只蚂蚁选择的任务序列
    iter_max =50  # 最大迭代次数
    profit = np.zeros(m)  # 每只蚂蚁的任务序列的总收益
    order_best = np.zeros((iter_max, n))  # 每次迭代的最优任务序列
    profit_best = np.zeros(iter_max)  # 每次迭代的最优收益
    profit_ave = np.zeros(iter_max)  # 每次迭代的平均收益
    iter_limit = 0  # 记录达到最优解的迭代次数


    # 给蚂蚁分配偏好
    ant_preferences = []
    for ant_idx in range(m):
        group = ant_idx % 3
        if group == 0:
            ant_preferences.append({
                "name": "value_first",
                "value_weight": 0.8,
                "energy_weight": 0.2,
            })
        elif group == 1:
            ant_preferences.append({
                "name": "energy_first",
                "value_weight": 0.2,
                "energy_weight": 0.8,
            })
        else:
            ant_preferences.append({
                "name": "balanced",
                "value_weight": 0.5,
                "energy_weight": 0.5,
            })



        # 多目标优化过渡版：收集候选解并维护 Pareto archive
    pareto_archive = []
    archive_size_history = np.zeros(iter_max)
    archive_best_value_history = np.zeros(iter_max)
    archive_min_energy_history = np.zeros(iter_max)

    # 控制迭代次数
    for iteration in range(iter_max):
        current_solutions = []   # 当前迭代中的候选解
        # 构建解空间
        tar_index = np.arange(1, n + 1)   #### 已更正
        # 每只蚂蚁依次选择任务
        for i in range(m):  ### 对于第i只蚂蚁
            preference = ant_preferences[i] # 每轮迭代中：第 i 只蚂蚁开始造路径时，先把它自己的偏好拿出来
            tau_current = tau_by_preference[preference["name"]]
            for j in range(n):
                tabu = table[i, :j]  # 禁忌表，记录已选任务  //数组切片操作，选取第i行0--j-1的所有元素。tabu返回的是形状为(j,)的一维数组
                allow_index = ~np.isin(tar_index, tabu)
                allow = tar_index[allow_index]  # 可用任务列表，即未被选择的任务
                tabu = tabu.astype(int)        ### 均转化为整型
                allow = allow.astype(int)


                # ### 计算选择概率  
                # p = np.copy(allow).astype(float)
                # for k in range(len(allow)):
                #     if len(tabu) == 0:
                #         metrics = evaluate_transition(0, allow[k], tar_info)
                #         heu_value = preference_heuristic(metrics, preference)
                #         p[k] = heu_value ** beta
                #     else:
                #         metrics = evaluate_transition(tabu[-1], allow[k], tar_info)
                #         heu_value = preference_heuristic(metrics, preference)
                #         p[k] = tau_current[int(tabu[-1]) - 1, int(allow[k]) - 1] ** alpha * heu_value ** beta
                

                ### 计算选择概率：对当前候选集合进行归一化多目标启发式评分
                candidate_metrics = []
                for candidate in allow:
                    if len(tabu) == 0:
                        metrics = evaluate_transition(0, candidate, tar_info)
                    else:
                        metrics = evaluate_transition(tabu[-1], candidate, tar_info)
                    candidate_metrics.append(metrics)

                mission_values = np.array([
                    metrics["mission_value"] if metrics["feasible"] else 0.0
                    for metrics in candidate_metrics
                ], dtype=float)

                system_energies = np.array([
                    metrics["system_energy"] if metrics["feasible"] else np.inf
                    for metrics in candidate_metrics
                ], dtype=float)

                feasible_mask = np.array([
                    metrics["feasible"] and np.isfinite(metrics["system_energy"])
                    for metrics in candidate_metrics
                ], dtype=bool)

                p = np.zeros(len(allow), dtype=float)

                if np.any(feasible_mask):
                    value_min = mission_values[feasible_mask].min()
                    value_max = mission_values[feasible_mask].max()
                    energy_min = system_energies[feasible_mask].min()
                    energy_max = system_energies[feasible_mask].max()

                    value_span = value_max - value_min
                    energy_span = energy_max - energy_min

                    value_weight = float(preference.get("value_weight", 0.5))
                    energy_weight = float(preference.get("energy_weight", 0.5))

                    for k in range(len(allow)):
                        if not feasible_mask[k]:
                            p[k] = 0.0
                            continue

                        if value_span > 0:
                            value_score = (mission_values[k] - value_min) / value_span
                        else:
                            value_score = 1.0

                        if energy_span > 0:
                            energy_score = (energy_max - system_energies[k]) / energy_span
                        else:
                            energy_score = 1.0

                        heu_value = value_weight * value_score + energy_weight * energy_score
                        heu_value = max(heu_value, 1e-8)

                        if len(tabu) == 0:
                            p[k] = heu_value ** beta
                        else:
                            pheromone = tau_current[int(tabu[-1]) - 1, int(allow[k]) - 1]
                            p[k] = pheromone ** alpha * heu_value ** beta






                ### 轮盘赌选择
                if np.sum(p) == 0:
                    break
                else:
                    p = p / np.sum(p)   ### 归一化
                    pc = np.cumsum(p)   ### 计算累计概率
                    target_index = np.where(pc >= np.random.rand())[0]  ### 随机选择/# 找到第一个累积概率≥随机数的位置
                    target = allow[target_index[0]]  # 根据概率选择的下一个任务
                    table[i, j] = target

            profit[i] = OrderProfit(table[i], tar_info)  # 第i只蚂蚁的任务序列的总收益，通过OrderProfit函数计算
   
            solution = evaluate_order(table[i], tar_info)
            solution["single_profit"] = float(profit[i])
            solution["iteration"] = int(iteration + 1)
            solution["ant_id"] = int(i + 1)
            solution["preference"] = ant_preferences[i]["name"]  # 判断多偏好蚂蚁是不是真的发挥作用

            if solution["target_count"] > 0:
                current_solutions.append(solution)
                

        pareto_current = get_pareto_front(current_solutions)

        # 计算最佳收益及平均收益
        if iteration == 0:   ### 如果是首个轮次
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


        ### 更新信息素：按偏好群体分别更新信息素矩阵
        share_rate = 0.3    # 跨种群信息素共享率 
        delta_tau_by_preference = {
            name: np.zeros((n, n)) for name in preference_names
        }

        if pareto_current:
            values = [solution["mission_value"] for solution in pareto_current]
            energies = [solution["system_energy"] for solution in pareto_current]

            value_min, value_max = min(values), max(values)
            energy_min, energy_max = min(energies), max(energies)

            for solution in pareto_current:
                sequence = solution["sequence"]
                if len(sequence) < 2:
                    continue

                if value_max > value_min:
                    value_norm = (solution["mission_value"] - value_min) / (value_max - value_min)
                else:
                    value_norm = 1.0

                if energy_max > energy_min:
                    energy_norm = (energy_max - solution["system_energy"]) / (energy_max - energy_min)
                else:
                    energy_norm = 1.0

                pheromone_score = max(0.1, 0.5 * value_norm + 0.5 * energy_norm)

                preference_name = solution.get("preference", "balanced")
                if preference_name not in delta_tau_by_preference:
                    preference_name = "balanced"

                for j in range(len(sequence) - 1):
                    a = int(sequence[j]) - 1
                    b = int(sequence[j + 1]) - 1

                    
                    for name in preference_names:
                        if name == preference_name:
                            delta_tau_by_preference[name][a, b] += q * pheromone_score
                        else:
                            delta_tau_by_preference[name][a, b] += q * share_rate * pheromone_score

        for name in preference_names:
            tau_by_preference[name] = (1 - vol) * tau_by_preference[name] + delta_tau_by_preference[name]
            tau_by_preference[name] = np.clip(tau_by_preference[name], tau_min, tau_max)
        


        pareto_archive = update_archive(
            pareto_archive,
            pareto_current,
            max_size=archive_max_size,
        )

        archive_size_history[iteration] = len(pareto_archive)

        if pareto_archive:
            archive_best_value_history[iteration] = max(
                solution["mission_value"] for solution in pareto_archive
            )
            archive_min_energy_history[iteration] = min(
                solution["system_energy"] for solution in pareto_archive
            )


        # === 信息素统计（调参观察用）===
        tau_all = np.stack([tau_by_preference[name] for name in preference_names])

        print(f"[iter {iteration+1:02d}] tau | "
              f"min={tau_all.min():.4f}  max={tau_all.max():.4f}  "
              f"mean={tau_all.mean():.4f}  std={tau_all.std():.4f}  "
              f"本轮Pareto解数={len(pareto_current)} | "
              f"全局Pareto解数={len(pareto_archive)}")
        # ================================


        table = np.zeros((m, n))  # table：清空路径表，为下一次迭代做准备

    task_profit, index = np.max(profit_best), np.argmax(profit_best)
    task = order_best[index]






    # print(f"选择的原始task是: {task}")


 


    # --- 在这里加入调试打印 ---

    #task = task[:np.where(task == 0)[0][0]]
    task = task.astype(int)
    # task = sorted(task)  ### 切片正序排序
    task = np.array(task)

    C = tar_info  # [序号, 经度, 维度, 高度, 重要程度, 过顶时刻, 滚转角, 俯仰角, 时间窗口]


    print("-" * 78)
    print("最优解任务规划迭代轮次:", iter_limit)
    print("Pareto archive 解数量:", len(pareto_archive))

    pareto_convergence = {
        "archive_size": archive_size_history,
        "best_mission_value": archive_best_value_history,
        "min_system_energy": archive_min_energy_history,
    }

    if return_pareto:
        return (
            task,
            task_profit,
            C,
            allTarget_time_windows,
            profit_best,
            profit_ave,
            iter_limit,
            pareto_archive,
            pareto_convergence,
        )

    # task_profit: 最大收益， task: 最佳任务序列，排序并去除末尾的 0， C: 任务计算信息  time_windows: 时间窗口
    return task, task_profit, C, allTarget_time_windows, profit_best, profit_ave, iter_limit
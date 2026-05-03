import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from utils.get_key_target_lib import get_key_target_lib
from utils.load_satellite import load_satellite
from utils.JulianDay import JulianDay
from utils.mission_planning_aco import mission_planning_aco
from utils.generate_output import generate_output, generate_pareto_output
from collections import Counter


def main():

    """修改前
    # 获取当前时间
    # current_time = datetime.now()
    start_time = datetime.now()   ##仅用来记录程序开始运行的时刻,计算总用时print('运行时间: ', end_time-start_time)
    current_time = datetime.now()
    # 计算任务规划开始时的儒略日值
    jd0 = JulianDay(current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)
    dt = 3600  # 时间步长, 单位秒
    print("当前时间: \n", current_time)
    """

    ### 修改开始时间为固定时刻
    start_time = datetime.now() # start_time 保持使用 now()，用来计算程序运行耗时没问题
    # ------------------ 修改这里 ------------------
    # 将 current_time 写死为固定的生成时刻 (Epoch)
    current_time = datetime(2026, 3, 5, 9, 18, 0)  
    # ----------------------------------------------
    # 计算任务规划开始时的儒略日值
    jd0 = JulianDay(current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)
    dt = 1200  # 时间步长, 单位秒
    print("设定的卫星初始基准时间: \n", current_time)


    """
    输入重点目标库经纬度
    :return: [序号, 名称, 经度, 维度, 高度, 重要程度]
    """
    key_target_lib = get_key_target_lib()
    #print("重点目标库: -- [序号, 经度, 维度, 高度, 重要程度]\n", key_target_lib)

    """
    卫星初始状态加载
    :return: 轨道位置及速度(x, y, z, dx, dy, dz), 轨道六根数oev0
    """
    rv0, oev0 = load_satellite()
    # 打印卫星初始状态信息: 卫星个数、数据维度、初始位置和速度
    print("卫星个数：\n", len(rv0))   ## len函数输出数组第一维的大小
    print("卫星轨道数据维度：\n", np.shape(rv0))
    print("卫星轨道初始位置和速度：\n", rv0)



    """
    执行任务规划算法
    参数: 重点目标库key_target_lib,
    """
    (
        task,
        profit,
        tar_info,
        allTarget_time_windows,
        profit_best,
        profit_ave,
        iter_limit,
        pareto_archive,
        pareto_convergence
    ) = mission_planning_aco(
        oev0,
        current_time,
        jd0,
        dt,
        rv0[0, 0:3],
        rv0[0, 3:6],
        key_target_lib,
        return_pareto=True
    )
   
   
   
   

    # ===  调试打印    ===

   # 如果task里有0，才进行切片
    if 0 in task:
        first_zero_index = np.where(task == 0)[0][0]
        # --- 在这里加入调试打印 ---
        # print(f"第一个0的索引是: {first_zero_index}")
        # -------------------------
        task = task[:first_zero_index]
    else:
        # 如果没有0，可以根据你的业务逻辑决定如何处理，这里我们先打印一下
        print("警告：task中没有0，无法进行切片。")
 

    # print("最佳任务目标序列:\n", task)
    # print("目标序列最大收益:\n", profit)
    # print("目标序列信息表: [序号, 经度, 维度, 高度, 重要程度, 过顶时刻, 滚转角, 俯仰角]\n", tar_info)
    # print("时间窗口:\n", allTarget_time_windows)
    print("Pareto解数量:\n", len(pareto_archive))


    if pareto_archive:

        best_value_solution = max(pareto_archive, key=lambda sol: sol["mission_value"])
        min_energy_solution = min(pareto_archive, key=lambda sol: sol["system_energy"])
        best_efficiency_solution = max(pareto_archive, key=lambda sol: sol["energy_efficiency"])



        # ## 计算折中方案
        # ideal_value = best_value_solution["mission_value"]
        # ideal_energy = min_energy_solution["system_energy"]


        # def normalized_distance_to_ideal(solution):
        #     value_range = max(sol["mission_value"] for sol in pareto_archive) - min(sol["mission_value"] for sol in pareto_archive)
        #     energy_range = max(sol["system_energy"] for sol in pareto_archive) - min(sol["system_energy"] for sol in pareto_archive)

        #     value_range = value_range if value_range > 0 else 1.0
        #     energy_range = energy_range if energy_range > 0 else 1.0

        #     value_dist = (ideal_value - solution["mission_value"]) / value_range
        #     energy_dist = (solution["system_energy"] - ideal_energy) / energy_range

        #     return np.sqrt(value_dist ** 2 + energy_dist ** 2)

        # compromise_solution = min(pareto_archive, key=normalized_distance_to_ideal)


        print("-" * 78)
        print("[最高任务价值方案]")
        print("任务价值:", best_value_solution["mission_value"])
        print("系统能耗:", best_value_solution["system_energy"])
        print("任务能效:", best_value_solution["energy_efficiency"])
        print("目标数量:", best_value_solution["target_count"])
        print("任务序列:", best_value_solution["sequence"])

        print("\n[最低系统能耗方案]")
        print("任务价值:", min_energy_solution["mission_value"])
        print("系统能耗:", min_energy_solution["system_energy"])
        print("任务能效:", min_energy_solution["energy_efficiency"])
        print("目标数量:", min_energy_solution["target_count"])
        print("任务序列:", min_energy_solution["sequence"])

        print("\n[最高任务能效方案/推荐方案]")
        print("任务价值:", best_efficiency_solution["mission_value"])
        print("系统能耗:", best_efficiency_solution["system_energy"])
        print("任务能效:", best_efficiency_solution["energy_efficiency"])
        print("目标数量:", best_efficiency_solution["target_count"])
        print("任务序列:", best_efficiency_solution["sequence"])

        # print("\n[折中推荐方案]")
        # print("任务价值:", compromise_solution["mission_value"])
        # print("系统能耗:", compromise_solution["system_energy"])
        # print("任务能效:", compromise_solution["energy_efficiency"])
        # print("目标数量:", compromise_solution["target_count"])
        # print("任务序列:", compromise_solution["sequence"])


        preference_counter = Counter(
            solution.get("preference", "unknown") for solution in pareto_archive
        )


        print("\n=== 推荐方案成像明细（最高任务能效方案）===")
        print(f"{'目标ID':>6}  {'过顶时刻(s)':>12}  {'可用时间(s)':>12}  {'成像时长(s)':>12}  {'任务价值':>10}  {'系统能耗':>10}")
        print("-" * 78)
        for item in best_efficiency_solution.get("exposure_plan", []):
            print(
                f"{int(item['target_id']):>6}  "
                f"{item['overhead_time']:>12.2f}  "
                f"{item['available_time'] if item['available_time'] != float('inf') else 9999.0:>12.2f}  "
                f"{item['exposure_time']:>12.2f}  "
                f"{item['mission_value']:>10.4f}  "
                f"{item['system_energy']:>10.4f}"
            )
        print("-" * 78)


        print("\nPareto解来源偏好分布:")
        for name, count in preference_counter.items():
            print(f"{name}: {count}")


    # print(f"历史最优收益变化: {list(profit_best)}")
    # print(f"各代平均收益变化: {list(profit_ave)}\n")
    ###  画图 
    # 1. 打印截断后的小数（np.round 本身就是安全的，不需要 copy）
    # print(f"\n历史最优: {np.round(profit_best, 2).tolist()}")
    # print(f"当代平均: {np.round(profit_ave, 2).tolist()}\n")

    # # 2. 画图
    # plt.plot(profit_best, marker='o', color='red', label='Best Profit')
    # plt.plot(profit_ave, marker='s', color='blue', linestyle='--', label='Average Profit')
    # plt.legend()
    
    # # 3. 直接保存图片并关闭
    # plt.savefig('/home/chujiaqing/newpro/gongda_mp/output/aco_convergence.png')
    # plt.close()


    if pareto_archive:
        pareto_energy = [solution["system_energy"] for solution in pareto_archive]
        pareto_value = [solution["mission_value"] for solution in pareto_archive]
        pareto_count = [solution["target_count"] for solution in pareto_archive]

        plt.figure()
        scatter = plt.scatter(
            pareto_energy,
            pareto_value,
            c=pareto_count,
            cmap="viridis",
            s=60,
            edgecolors="black",
            linewidths=0.5,
        )
        plt.xlabel("System Energy")
        plt.ylabel("Mission Value")
        plt.title("Pareto Front: Mission Value vs System Energy")


        plt.colorbar(scatter, label="Target Count")
        plt.grid(True, linestyle="--", alpha=0.4)
        plt.tight_layout()
        plt.savefig("/home/chujiaqing/newpro/gongda_mp/output/pareto_front.png")
        plt.close()

    if pareto_convergence:
        plt.figure()
        plt.plot(
            pareto_convergence["archive_size"],
            marker="o",
            color="purple",
            label="Pareto Archive Size",
        )
        plt.xlabel("Iteration")
        plt.ylabel("Archive Size")
        plt.title("Pareto Archive Size Convergence")
        plt.grid(True, linestyle="--", alpha=0.4)
        plt.legend()
        plt.tight_layout()
        plt.savefig("/home/chujiaqing/newpro/gongda_mp/output/pareto_archive_size.png")
        plt.close()

        plt.figure()
        plt.plot(
            pareto_convergence["best_mission_value"],
            marker="o",
            color="green",
            label="Best Mission Value",
        )

        plt.plot(
            pareto_convergence["min_system_energy"],
            marker="s",
            color="orange",
            linestyle="--",
            label="Min System Energy",
        )

        plt.xlabel("Iteration")
        plt.title("Pareto Convergence: Mission Value and System Energy")

        plt.grid(True, linestyle="--", alpha=0.4)
        plt.legend()
        plt.tight_layout()
        plt.savefig("/home/chujiaqing/newpro/gongda_mp/output/pareto_objectives_convergence.png")
        plt.close()

    # ===  调试打印    ===


    if pareto_archive:
        selected_solution = best_efficiency_solution
        selected_task = selected_solution["sequence"]
        selected_profit = selected_solution["mission_value"]
    else:
        selected_task = task
        selected_profit = profit

    target_time_windows = {
        int(k): allTarget_time_windows[k]
        for k in selected_task
        if k in allTarget_time_windows
    }

    output_path = "/home/chujiaqing/newpro/gongda_mp/output/output.json"
    generate_output(selected_task, selected_profit, tar_info, target_time_windows, output_path)
    
    
    ## 输出帕累托
    pareto_output_path = "/home/chujiaqing/newpro/gongda_mp/output/pareto_output.json"
    generate_pareto_output(
        pareto_archive,
        tar_info,
        allTarget_time_windows,
        pareto_output_path
    )

    end_time = datetime.now()
    print('运行时间: ', end_time-start_time)



if __name__ == '__main__':
    main()

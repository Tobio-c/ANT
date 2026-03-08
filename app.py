import numpy as np
from datetime import datetime
from utils.get_key_target_lib import get_key_target_lib
from utils.load_satellite import load_satellite
from utils.JulianDay import JulianDay
from utils.mission_planning_aco import mission_planning_aco
from utils.generate_output import generate_output
def main():
    # 获取当前时间
    # current_time = datetime.now()
    start_time = datetime.now()
    current_time = datetime.now()
    # 计算任务规划开始时的儒略日值
    jd0 = JulianDay(current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)
    dt = 900  # 时间步长, 单位秒
    print("当前时间: \n", current_time)


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
    print("卫星个数：\n", len(rv0))
    print("卫星轨道数据维度：\n", np.shape(rv0))
    print("卫星轨道初始位置和速度：\n", rv0)


    """
    执行任务规划算法
    参数: 重点目标库key_target_lib,
    """
    task, profit, tar_info, allTarget_time_windows = mission_planning_aco(oev0, current_time, jd0, dt, rv0[0, 0:3], rv0[0, 3:6], key_target_lib)
    print("最佳任务目标序列:\n", task)
    print("目标序列最大收益:\n", profit)
    # print("目标序列信息表: [序号, 经度, 维度, 高度, 重要程度, 过顶时刻, 滚转角, 俯仰角]\n", tar_info)
    # print("时间窗口:\n", allTarget_time_windows)

    # 只取待观测目标点的时间窗口进行下传
    target_time_windows = {int(k): allTarget_time_windows[k] for k in task if k in allTarget_time_windows}
    """
    生成json输出文件
    """

    ######output_path = "D:\SoftWare\PythonCode\gongda_mp\output.json"
    output_path = "/home/chujiaqing/newpro/gongda_mp/output/output.json"
    generate_output(task, profit, tar_info, target_time_windows, output_path)  # 只下注目标任务序列包含的目标点的可见时间窗口
    end_time = datetime.now()
    print('运行时间: ', end_time-start_time)

if __name__ == '__main__':
    main()

import numpy as np
import json
def get_key_target_lib():
    # 读取 task_list.json 文件
    ###### with open('D:\SoftWare\PythonCode\gongda_mp//task_list.json', 'r', encoding='utf-8') as f:
    with open('/home/chujiaqing/newpro/gongda_mp/task_list.json', 'r', encoding='utf-8') as f:
        task_data = json.load(f)

    # 提取经纬度信息
    key_target_list = []
    for target in task_data['targetList']:
        lon = float(target['longitude']) if target['longitude'] is not None else None
        lat = float(target['latitude']) if target['latitude'] is not None else None
        if lon is not None and lat is not None:
            key_target_list.append([lon, lat])



    # key_target_list = np.array(key_target_list)
    ### 减少目标数，截取前四十个
    key_target_list = np.array(key_target_list)[:40]

    # 定义各目标点高度、重要程度
    target_nums = len(key_target_list)
    height = np.zeros((target_nums, 1))
    target_values = 0.5 + 0.5 * np.random.rand(target_nums, 1)  # 这里为随机设置各目标的重要程度
    # 数组形式：[序号, 经度, 维度, 高度, 重要程度]
    key_target_lib = np.column_stack(((np.arange(1, target_nums + 1)).reshape(-1, 1), key_target_list[:, 0] * np.pi/180, key_target_list[:, 1] * np.pi/180, height, target_values))
    return key_target_lib   ##返回（N，5）的数据
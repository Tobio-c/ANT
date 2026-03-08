import json
import os
import numpy as np
from datetime import datetime, date


def convert_ndarray(obj):
    """递归转换所有不可序列化对象为可序列化类型"""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()  # 处理日期时间对象
    elif isinstance(obj, list):
        return [convert_ndarray(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_ndarray(v) for k, v in obj.items()}
    elif hasattr(obj, '__dict__'):  # 处理自定义对象
        return convert_ndarray(obj.__dict__)
    else:
        try:
            # 尝试转换为普通Python类型
            return float(obj) if isinstance(obj, np.number) else obj
        except (ValueError, TypeError):
            return str(obj)  # 作为最后的手段转换为字符串


def generate_output(task, profit, tar_info, time_windows, output_path):
    try:
        # 先递归转换tar_info中的所有ndarray
        tar_info = convert_ndarray(tar_info)

        output_data = {
            "mission_info": {
                "algorithm": "ACO",
                "total_profit": float(profit),
                "target_count": len(task),
                "target_sequence": task,
                "time_windows": time_windows
            },
            "target_details": []
        }
        # 写入卫星信息数据
        for target in tar_info:
            if len(target) >= 7:
                target_data = {
                    "id": int(target[0]),
                    "longitude": float(target[1]),
                    "latitude": float(target[2]),
                    "altitude": float(target[3]),
                    "importance": float(target[4]),
                    "overhead_time": str(target[5]),
                    "roll_angle": float(target[6]),
                    "pitch_angle": float(target[7]) if len(target) > 7 else 0.0
                }
                output_data["target_details"].append(target_data)

        # 使用自定义序列化器处理任何剩余的不可序列化对象
        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, np.generic):
                    return obj.item()  # 处理NumPy标量
                elif isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                return super().default(obj)

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)

        print(f"JSON 输出文件已生成: {output_path}")

    except Exception as e:
        print(f"生成输出文件时出错: {e}")
        # 打印详细的错误信息，帮助诊断问题
        import traceback
        traceback.print_exc()
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


def build_pareto_solution_data(solution, time_windows):
    sequence = [int(target_id) for target_id in solution.get("sequence", [])]

    solution_time_windows = {
        int(target_id): time_windows[target_id]
        for target_id in sequence
        if target_id in time_windows
    }

    return {
        "preference": solution.get("preference", "unknown"),
        "iteration": int(solution.get("iteration", 0)),
        "ant_id": int(solution.get("ant_id", 0)),
        "target_count": int(solution.get("target_count", len(sequence))),
        "target_sequence": sequence,
        "objectives": {
            "mission_value": float(solution.get("mission_value", 0.0)),
            "system_energy": float(solution.get("system_energy", 0.0)),
            "energy_efficiency": float(solution.get("energy_efficiency", 0.0)),
        },
        "energy_breakdown": {
            "maneuver_energy": float(solution.get("maneuver_energy", 0.0)),
            "payload_energy": float(solution.get("payload_energy", 0.0)),
            "idle_energy": float(solution.get("idle_energy", 0.0)),
        },
        "time_metrics": {
            "maneuver_time": float(solution.get("maneuver_time", 0.0)),
            "total_time": float(solution.get("total_time", 0.0)),
        },
        "single_profit": float(solution.get("single_profit", 0.0)),
        "time_windows": convert_ndarray(solution_time_windows),
        "exposure_plan": convert_ndarray(solution.get("exposure_plan", [])),
    }


def generate_pareto_output(pareto_archive, tar_info, time_windows, output_path):
    try:
        pareto_solutions = []

        for rank, solution in enumerate(pareto_archive, start=1):
            solution_data = build_pareto_solution_data(solution, time_windows)
            solution_data["rank"] = rank
            pareto_solutions.append(solution_data)

        target_details = []
        converted_tar_info = convert_ndarray(tar_info)

        for target in converted_tar_info:
            if len(target) >= 7:
                target_details.append({
                    "id": int(target[0]),
                    "longitude": float(target[1]),
                    "latitude": float(target[2]),
                    "altitude": float(target[3]),
                    "importance": float(target[4]),
                    "overhead_time": str(target[5]),
                    "roll_angle": float(target[6]),
                    "pitch_angle": float(target[7]) if len(target) > 7 else 0.0
                })

        output_data = {
            "mission_info": {
                "algorithm": "MOACO",
                "solution_count": len(pareto_solutions),
                "objectives": [
                    {
                        "name": "mission_value",
                        "direction": "max"
                    },
                    {
                        "name": "system_energy",
                        "direction": "min"
                    }
                ]
            },
            "pareto_solutions": pareto_solutions,
            "target_details": target_details
        }

        class NumpyEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, np.generic):
                    return obj.item()
                elif isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                return super().default(obj)

        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2, cls=NumpyEncoder)

        print(f"Pareto JSON 输出文件已生成: {output_path}")

    except Exception as e:
        print(f"生成 Pareto 输出文件时出错: {e}")
        import traceback
        traceback.print_exc()
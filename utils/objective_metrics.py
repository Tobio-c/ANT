import numpy as np

from utils.ManeuverTime import ManeuverTime
from utils.NextProfit import DELTA, T_EXP_MIN, ETA, optimal_exposure, image_quality_gain



ROLL_ENERGY_COEF = 0.05
PAYLOAD_ENERGY_COEF = ETA
IDLE_ENERGY_COEF = 0.002


def normalize_sequence(order):
    order = np.asarray(order).astype(int).tolist()
    if 0 in order:
        order = order[:order.index(0)]
    return [target_id for target_id in order if target_id > 0]


def calc_target_value(importance, exposure_time):
    if exposure_time < T_EXP_MIN or importance <= 0:
        return 0.0
    return float(image_quality_gain(importance, exposure_time))


def calc_maneuver_energy(angle1, angle2):
    delta_angle_deg = abs(angle1 - angle2) * 180.0 / np.pi
    return float(ROLL_ENERGY_COEF * delta_angle_deg)


def calc_payload_energy(exposure_time):
    return float(PAYLOAD_ENERGY_COEF * max(exposure_time, 0.0))


def calc_idle_energy(wait_time):
    return float(IDLE_ENERGY_COEF * max(wait_time, 0.0))


def evaluate_transition(prev_target_id, target_id, tar_info):
    target_idx = int(target_id) - 1

    importance = 3.0 * float(tar_info[target_idx, 4])
    overhead_time = float(tar_info[target_idx, 5])
    roll_angle = float(tar_info[target_idx, 6])

    if prev_target_id == 0:
        maneuver_time = 0.0
        maneuver_energy = calc_maneuver_energy(0.0, roll_angle)
        wait_time = max(overhead_time, 0.0)
        available_time = float("inf")
    else:
        prev_idx = int(prev_target_id) - 1
        prev_overhead_time = float(tar_info[prev_idx, 5])
        prev_roll_angle = float(tar_info[prev_idx, 6])

        maneuver_time = float(ManeuverTime(prev_roll_angle, roll_angle))
        time_gap = overhead_time - prev_overhead_time
        wait_time = max(time_gap - maneuver_time, 0.0)
        available_time = time_gap - maneuver_time
        maneuver_energy = calc_maneuver_energy(prev_roll_angle, roll_angle)

    idle_energy = calc_idle_energy(wait_time)

    if importance <= 0 or available_time < T_EXP_MIN:
        return {
            "from_target": int(prev_target_id),
            "target_id": int(target_id),
            "feasible": False,
            "mission_value": 0.0,
            "system_energy": float("inf"),
            "maneuver_energy": float(maneuver_energy),
            "payload_energy": 0.0,
            "idle_energy": float(idle_energy),
            "maneuver_time": float(maneuver_time),
            "wait_time": float(wait_time),
            "available_time": float(available_time),
            "exposure_time": 0.0,
            "overhead_time": overhead_time,
            "roll_angle": roll_angle,
        }

    exposure_time = optimal_exposure(available_time, importance)
    mission_value = calc_target_value(importance, exposure_time)
    payload_energy = calc_payload_energy(exposure_time)
    system_energy = maneuver_energy + payload_energy + idle_energy

    return {
        "from_target": int(prev_target_id),
        "target_id": int(target_id),
        "feasible": True,
        "mission_value": float(mission_value),
        "system_energy": float(system_energy),
        "maneuver_energy": float(maneuver_energy),
        "payload_energy": float(payload_energy),
        "idle_energy": float(idle_energy),
        "maneuver_time": float(maneuver_time),
        "wait_time": float(wait_time),
        "available_time": float(available_time),
        "exposure_time": float(exposure_time),
        "overhead_time": overhead_time,
        "roll_angle": roll_angle,
    }


def evaluate_order(order, tar_info):
    sequence = normalize_sequence(order)

    total_value = 0.0
    total_energy = 0.0
    total_maneuver_energy = 0.0
    total_payload_energy = 0.0
    total_idle_energy = 0.0
    total_maneuver_time = 0.0

    exposure_plan = []
    feasible = True
    prev_target_id = 0

    for target_id in sequence:
        metrics = evaluate_transition(prev_target_id, target_id, tar_info)

        if not metrics["feasible"]:
            feasible = False
            break

        total_value += metrics["mission_value"]
        total_energy += metrics["system_energy"]
        total_maneuver_energy += metrics["maneuver_energy"]
        total_payload_energy += metrics["payload_energy"]
        total_idle_energy += metrics["idle_energy"]
        total_maneuver_time += metrics["maneuver_time"]

        exposure_plan.append(metrics)
        prev_target_id = target_id

    if exposure_plan:
        total_time = exposure_plan[-1]["overhead_time"] - exposure_plan[0]["overhead_time"]
    else:
        total_time = 0.0

    if feasible and total_energy > 0:
        energy_efficiency = total_value / total_energy
    else:
        energy_efficiency = 0.0

    return {
        "sequence": sequence[:len(exposure_plan)],
        "feasible": feasible,
        "mission_value": float(total_value),
        "system_energy": float(total_energy),
        "energy_efficiency": float(energy_efficiency),
        "maneuver_energy": float(total_maneuver_energy),
        "payload_energy": float(total_payload_energy),
        "idle_energy": float(total_idle_energy),
        "maneuver_time": float(total_maneuver_time),
        "total_time": float(max(total_time, 0.0)),
        "target_count": len(exposure_plan),
        "exposure_plan": exposure_plan,
    }


def preference_heuristic(metrics, preference):
    if not metrics["feasible"]:
        return 0.0

    mission_value = float(metrics["mission_value"])
    system_energy = float(metrics["system_energy"])

    value_weight = float(preference.get("value_weight", 0.5))
    energy_weight = float(preference.get("energy_weight", 0.5))

    # 能耗越小越好，所以转成节能得分
    energy_score = 1.0 / (1.0 + system_energy)

    score = value_weight * mission_value + energy_weight * energy_score
    return max(score, 1e-8)
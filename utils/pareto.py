import numpy as np


DEFAULT_OBJECTIVES = (
    ("mission_value", "max"),
    ("system_energy", "min"),
)


MIN_TARGET_COUNT = 6        ## 最低系统能耗方案目标数下限
MIN_MISSION_VALUE = 15.0    ## 最低系统能耗方案目标价值下限

def is_valid_solution(solution):
    return (
        solution.get("feasible", True)
        and np.isfinite(float(solution.get("system_energy", float("inf"))))
        and solution.get("target_count", 0) >= MIN_TARGET_COUNT
        and float(solution.get("mission_value", 0.0)) >= MIN_MISSION_VALUE
    )



## 判断解 A 是否支配解 B。
def dominates(solution_a, solution_b, objectives=DEFAULT_OBJECTIVES):
    if not is_valid_solution(solution_a):
        return False
    if not is_valid_solution(solution_b):
        return True

    better_or_equal = True
    strictly_better = False

    for key, direction in objectives:
        value_a = float(solution_a[key])
        value_b = float(solution_b[key])

        if direction == "max":
            if value_a < value_b:
                better_or_equal = False
                break
            if value_a > value_b:
                strictly_better = True
        elif direction == "min":
            if value_a > value_b:
                better_or_equal = False
                break
            if value_a < value_b:
                strictly_better = True
        else:
            raise ValueError(f"Unsupported objective direction: {direction}")

    return better_or_equal and strictly_better


def solution_signature(solution):
    return tuple(int(target_id) for target_id in solution.get("sequence", []))


def deduplicate_solutions(solutions, objectives=DEFAULT_OBJECTIVES):
    best_by_sequence = {}

    for solution in solutions:
        if not is_valid_solution(solution):
            continue

        signature = solution_signature(solution)

        if signature not in best_by_sequence:
            best_by_sequence[signature] = solution
        elif dominates(solution, best_by_sequence[signature], objectives):
            best_by_sequence[signature] = solution

    return list(best_by_sequence.values())


## 从所有候选解中筛出非支配解。     
def get_pareto_front(solutions, objectives=DEFAULT_OBJECTIVES):
    candidates = deduplicate_solutions(solutions, objectives)
    pareto_front = []

    for i, solution_i in enumerate(candidates):
        dominated = False

        for j, solution_j in enumerate(candidates):
            if i == j:
                continue

            if dominates(solution_j, solution_i, objectives):
                dominated = True
                break

        if not dominated:
            pareto_front.append(solution_i)

    return pareto_front

## 拥挤距离用于保持帕累托解分布均匀。
def crowding_distance(solutions, objectives=DEFAULT_OBJECTIVES):
    if not solutions:
        return []

    distances = [0.0] * len(solutions)

    if len(solutions) <= 2:
        return [float("inf")] * len(solutions)

    for key, _ in objectives:
        sorted_indices = sorted(
            range(len(solutions)),
            key=lambda idx: float(solutions[idx][key])
        )

        distances[sorted_indices[0]] = float("inf")
        distances[sorted_indices[-1]] = float("inf")

        min_value = float(solutions[sorted_indices[0]][key])
        max_value = float(solutions[sorted_indices[-1]][key])
        span = max_value - min_value

        if span == 0:
            continue

        for rank in range(1, len(sorted_indices) - 1):
            prev_value = float(solutions[sorted_indices[rank - 1]][key])
            next_value = float(solutions[sorted_indices[rank + 1]][key])
            distances[sorted_indices[rank]] += abs(next_value - prev_value) / span

    return distances


def truncate_by_crowding_distance(solutions, max_size, objectives=DEFAULT_OBJECTIVES):
    if max_size is None or len(solutions) <= max_size:
        return solutions

    distances = crowding_distance(solutions, objectives)
    ranked_indices = sorted(
        range(len(solutions)),
        key=lambda idx: distances[idx],
        reverse=True
    )

    return [solutions[idx] for idx in ranked_indices[:max_size]]


def update_archive(archive, new_solutions, max_size=None, objectives=DEFAULT_OBJECTIVES):
    merged_solutions = list(archive) + list(new_solutions)
    pareto_front = get_pareto_front(merged_solutions, objectives)
    return truncate_by_crowding_distance(pareto_front, max_size, objectives)
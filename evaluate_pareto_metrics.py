#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path


def load_pareto_points(json_path: Path):
    data = json.loads(json_path.read_text(encoding="utf-8"))
    sols = data.get("pareto_solutions", [])
    points = []
    for s in sols:
        obj = s.get("objectives", {})
        mv = float(obj.get("mission_value", 0.0))
        se = float(obj.get("system_energy", math.inf))
        if math.isfinite(mv) and math.isfinite(se):
            points.append({"mission_value": mv, "system_energy": se})
    return points


def dominates(a, b):
    # 目标方向: mission_value(max), system_energy(min)
    better_or_equal = (
        a["mission_value"] >= b["mission_value"]
        and a["system_energy"] <= b["system_energy"]
    )
    strictly_better = (
        a["mission_value"] > b["mission_value"]
        or a["system_energy"] < b["system_energy"]
    )
    return better_or_equal and strictly_better


def non_dominated(points):
    nd = []
    for i, p in enumerate(points):
        dom = False
        for j, q in enumerate(points):
            if i != j and dominates(q, p):
                dom = True
                break
        if not dom:
            nd.append(p)
    # 去重
    uniq = {(p["mission_value"], p["system_energy"]): p for p in nd}
    return list(uniq.values())


def compute_reference_point(points, margin_ratio=0.05):
    mv_vals = [p["mission_value"] for p in points]
    se_vals = [p["system_energy"] for p in points]
    mv_min, mv_max = min(mv_vals), max(mv_vals)
    se_min, se_max = min(se_vals), max(se_vals)

    mv_span = max(mv_max - mv_min, 1e-9)
    se_span = max(se_max - se_min, 1e-9)

    # 对(max, min)目标，参考点需更差：mission_value更小、system_energy更大
    ref_mv = mv_min - margin_ratio * mv_span
    ref_se = se_max + margin_ratio * se_span
    return ref_mv, ref_se


def hypervolume_2d(points, ref_mv, ref_se):
    """
    2D Hypervolume for:
      - mission_value: maximize
      - system_energy: minimize
    """
    if not points:
        return 0.0

    nd = non_dominated(points)
    nd_sorted = sorted(nd, key=lambda p: p["mission_value"])

    hv = 0.0
    prev_mv = ref_mv
    best_se_so_far = ref_se

    for p in nd_sorted:
        mv = p["mission_value"]
        se = min(p["system_energy"], best_se_so_far)

        width = mv - prev_mv
        height = ref_se - se

        if width > 0 and height > 0:
            hv += width * height

        prev_mv = max(prev_mv, mv)
        best_se_so_far = min(best_se_so_far, se)

    return hv


def normalize_points(points):
    if not points:
        return []
    mv_vals = [p["mission_value"] for p in points]
    se_vals = [p["system_energy"] for p in points]

    mv_min, mv_max = min(mv_vals), max(mv_vals)
    se_min, se_max = min(se_vals), max(se_vals)

    mv_span = max(mv_max - mv_min, 1e-9)
    se_span = max(se_max - se_min, 1e-9)

    norm = []
    for p in points:
        # mission_value: 越大越好
        x = (p["mission_value"] - mv_min) / mv_span
        # system_energy: 越小越好 -> 反向归一化
        y = (se_max - p["system_energy"]) / se_span
        norm.append((x, y))
    return norm


def spacing(points):
    """
    Schott Spacing:
    最近邻距离的标准差（基于归一化后目标空间）。
    值越小通常表示前沿分布越均匀。
    """
    if len(points) <= 1:
        return 0.0

    nd = non_dominated(points)
    if len(nd) <= 1:
        return 0.0

    norm = normalize_points(nd)
    dists = []

    for i, p in enumerate(norm):
        nearest = math.inf
        for j, q in enumerate(norm):
            if i == j:
                continue
            d = math.dist(p, q)
            if d < nearest:
                nearest = d
        dists.append(nearest)

    d_bar = sum(dists) / len(dists)
    if len(dists) == 1:
        return 0.0

    return math.sqrt(sum((d - d_bar) ** 2 for d in dists) / (len(dists) - 1))


def main():
    parser = argparse.ArgumentParser(description="Evaluate Pareto set metrics: HV and Spacing")
    parser.add_argument(
        "--input",
        default="/home/chujiaqing/newpro/gongda_mp/output/pareto_output.json",
        help="Path to pareto_output.json",
    )
    parser.add_argument("--ref-mv", type=float, default=None, help="Reference mission_value (worse point)")
    parser.add_argument("--ref-se", type=float, default=None, help="Reference system_energy (worse point)")
    parser.add_argument("--margin", type=float, default=0.05, help="Auto reference margin ratio")
    args = parser.parse_args()

    points = load_pareto_points(Path(args.input))
    nd = non_dominated(points)

    if not nd:
        print("No valid Pareto points found.")
        return

    if args.ref_mv is None or args.ref_se is None:
        ref_mv, ref_se = compute_reference_point(nd, margin_ratio=args.margin)
    else:
        ref_mv, ref_se = args.ref_mv, args.ref_se

    hv = hypervolume_2d(nd, ref_mv, ref_se)
    sp = spacing(nd)

    print("=== Pareto Evaluation ===")
    print(f"Input file: {args.input}")
    print(f"Point count (raw): {len(points)}")
    print(f"Point count (non-dominated): {len(nd)}")
    print(f"Reference point: mission_value={ref_mv:.6f}, system_energy={ref_se:.6f}")
    print(f"Hypervolume (HV): {hv:.6f}")
    print(f"Spacing: {sp:.6f}")


if __name__ == "__main__":
    main()
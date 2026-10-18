# -*- coding: utf-8 -*-
"""
评审整改表格自动生成（C2 / M7 主网格 + 摘要/结论数字）
====================================================
读取 run_review_experiments.py main 输出的 exp_results/ablation_multi_seed_v2.csv
（16 配置 × 8 种子 × 4 方案，含 recall/sem/bit 的 final-step 均值±种子std 与
recall_ep/bit_ep 的回合级均值±种子std），生成：
  - TABLE IV  Recall@high vs ρ (σ_est = 1.2 dB)
  - TABLE V   Recall@high vs σ_est (ρ = 0.85)
  - TABLE VI  Grid-mean 汇总（跨 16 配置均值 ± 跨配置 std）
  - 摘要 / 结论需要覆盖的“修正后”数字串
  - M7 回合级汇总（recall_ep / bit_ep）

用法：
  python make_review_tables.py            # 打印 markdown 片段到 stdout
  python make_review_tables.py --write    # 同时写到 exp_results/review_tables_v2.md
"""
import argparse
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = os.path.join(HERE, "exp_results")
CSV_MAIN = os.path.join(SAVE_DIR, "ablation_multi_seed_v2.csv")

METHODS = ["PPO (policy gradient)", "Double-DQN", "Fixed policy", "EqualGran"]
# CSV 列前缀对应的方案键
KEYS = {"PPO (policy gradient)": "PPO", "Double-DQN": "DQN",
        "Fixed policy": "Fixed", "EqualGran": "EqualGran"}

RHO_LIST = [0.5, 0.7, 0.85, 0.95]
SIG_LIST = [0.0, 0.6, 1.2, 2.0]

# 复杂度常量（不随重训变化，来自 Table III / complexity.csv）
CONST = {
    "PPO (policy gradient)": ("37,395", "2.329"),
    "Double-DQN": ("109,248", "0.138"),
    "Fixed policy": ("0", "negligible"),
    "EqualGran": ("0", "negligible"),
}


def fmt(x, dp=3):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    return f"{x:.{dp}f}"


def load_main():
    if not os.path.exists(CSV_MAIN):
        raise SystemExit(f"找不到 {CSV_MAIN}：请先跑完 run_review_experiments.py main")
    df = pd.read_csv(CSV_MAIN)
    # 兼容：只取 tag=='full'（main 仅 full）；若列含 tag 则过滤
    if "tag" in df.columns:
        df = df[df["tag"].astype(str) == "full"]
    return df


def grid_tableIV(df):
    sub = df[np.isclose(df["sigma_est"], 1.2)]
    sub = sub.sort_values("rho")
    lines = ["| Method | " + " | ".join(f"ρ = {r}" for r in RHO_LIST) + " |",
             "|" + "---|" * (len(RHO_LIST) + 1)]
    for m in METHODS:
        k = KEYS[m]
        row = [m]
        for r in RHO_LIST:
            cell = sub[np.isclose(sub["rho"], r)]
            if len(cell) == 0:
                row.append("—")
            else:
                mu = cell.iloc[0][f"{k}_recall_mean"]
                sd = cell.iloc[0][f"{k}_recall_std"]
                row.append(f"{fmt(mu)} ± {fmt(sd)}")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def grid_tableV(df):
    sub = df[np.isclose(df["rho"], 0.85)]
    sub = sub.sort_values("sigma_est")
    lines = ["| Method | " + " | ".join(f"σ_est = {s}" for s in SIG_LIST) + " |",
             "|" + "---|" * (len(SIG_LIST) + 1)]
    for m in METHODS:
        k = KEYS[m]
        row = [m]
        for s in SIG_LIST:
            cell = sub[np.isclose(sub["sigma_est"], s)]
            if len(cell) == 0:
                row.append("—")
            else:
                mu = cell.iloc[0][f"{k}_recall_mean"]
                sd = cell.iloc[0][f"{k}_recall_std"]
                row.append(f"{fmt(mu)} ± {fmt(sd)}")
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def grid_tableVI(df):
    lines = ["| Method | Recall@high | Semantic utility/step | Bits/step | Params | Latency (ms/step) |",
             "|---|---|---|---|---|---|"]
    # 跨 16 配置：grid_mean = mean(per-config seed-mean)；grid_std = std(per-config seed-mean)
    for m in METHODS:
        k = KEYS[m]
        rm = df[f"{k}_recall_mean"].mean()
        rs = df[f"{k}_recall_mean"].std(ddof=1)
        sm = df[f"{k}_sem_mean"].mean()
        ss = df[f"{k}_sem_mean"].std(ddof=1)
        bm = df[f"{k}_bit_mean"].mean()
        bs = df[f"{k}_bit_mean"].std(ddof=1)
        params, lat = CONST.get(m, ("—", "—"))
        line = (f"| {m} | {fmt(rm)} ± {fmt(rs)} | {fmt(sm)} ± {fmt(ss)} | "
                f"{fmt(bm,1)} ± {fmt(bs,1)} | {params} | {lat} |")
        lines.append(line)
    return "\n".join(lines), df


def summary_numbers(df):
    out = {}
    for m in METHODS:
        k = KEYS[m]
        out[m] = dict(
            recall_mean=df[f"{k}_recall_mean"].mean(),
            bit_mean=df[f"{k}_bit_mean"].mean(),
            recall_ep_mean=df[f"{k}_recall_ep_mean"].mean() if f"{k}_recall_ep_mean" in df else None,
            bit_ep_mean=df[f"{k}_bit_ep_mean"].mean() if f"{k}_bit_ep_mean" in df else None,
        )
    return out


def m7_block(df):
    lines = ["**M7 回合级总任务价值（基于 6 元组评估）**", "",
             "| Method | 回合平均 Recall@high | 回合总 Bits/step (mean) |",
             "|---|---|---|"]
    for m in METHODS:
        k = KEYS[m]
        rem = df[f"{k}_recall_ep_mean"].mean()
        bem = df[f"{k}_bit_ep_mean"].mean()
        lines.append(f"| {m} | {fmt(rem)} | {fmt(bem,1)} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    df = load_main()

    t4 = grid_tableIV(df)
    t5 = grid_tableV(df)
    t6, _ = grid_tableVI(df)
    nums = summary_numbers(df)
    m7 = m7_block(df)

    ppo_r = nums["PPO (policy gradient)"]["recall_mean"]
    dqn_r = nums["Double-DQN"]["recall_mean"]
    eq_r = nums["EqualGran"]["recall_mean"]
    ppo_b = nums["PPO (policy gradient)"]["bit_mean"]
    dqn_b = nums["Double-DQN"]["bit_mean"]
    eq_b = nums["EqualGran"]["bit_mean"]

    abstract_str = (
        f"[摘要修正后数字] PPO grid-mean Recall@high = {fmt(ppo_r)}, "
        f"Double-DQN = {fmt(dqn_r)}, EqualGran = {fmt(eq_r)}; "
        f"bits/step: PPO = {fmt(ppo_b,1)}, DQN = {fmt(dqn_b,1)}, EqualGran = {fmt(eq_b,1)}. "
        f"学习效率 ≈ {fmt(ppo_b/eq_b*100,0)}% (PPO) / {fmt(dqn_b/eq_b*100,0)}% (DQN) 的比特成本达到 EqualGran 召回。"
    )

    out = []
    out.append("## TABLE IV. Recall@high versus ρ (σ_est = 1.2 dB)\n")
    out.append(t4 + "\n")
    out.append("## TABLE V. Recall@high versus σ_est (in dB) (ρ = 0.85, corrected reward)\n")
    out.append(t5 + "\n")
    out.append("## TABLE VI. Grid-mean performance summary (16 configurations × 8 seeds, greedy evaluation, corrected reward)\n")
    out.append(t6 + "\n")
    out.append("## M7 回合级指标\n")
    out.append(m7 + "\n")
    out.append("## 摘要/结论待覆盖数字\n")
    out.append(abstract_str + "\n")

    text = "\n".join(out)
    print(text)
    if args.write:
        path = os.path.join(SAVE_DIR, "review_tables_v2.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\n[written] {path}")


if __name__ == "__main__":
    main()

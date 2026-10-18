# -*- coding: utf-8 -*-
mp = "output/ieee-uav-semantic-ppo-20261014/stage1/final_draft.md"
text = open(mp, encoding="utf-8").read()

def rep(old, new):
    global text
    assert text.count(old) == 1, f"count({old[:60]!r})={text.count(old)}"
    text = text.replace(old, new)

def rep_line(anchor, new):
    global text
    lines = text.split("\n")
    hits = [i for i, l in enumerate(lines) if anchor in l]
    assert len(hits) == 1, f"anchor {anchor[:40]!r} hits={len(hits)}"
    lines[hits[0]] = new
    text = "\n".join(lines)

# ---------- VI-A / VI-B ----------
rep("Table IV reports Recall@high as a function of the channel correlation coefficient ρ at a fixed CSI noise level σ_est = 1.2 dB.",
    "Table IV reports Recall@high (mean ± sample standard deviation over three seeds) as a function of the channel correlation coefficient ρ at a fixed CSI noise level σ_est = 1.2 dB, under the corrected reward.")

rep("### B. Recall versus CSI Noise σ_est",
    "Both learned agents respond to channel correlation, but in different ways. The Double-DQN recall rises monotonically from 0.252 at ρ = 0.5 to 0.330 at ρ = 0.95, whereas the PPO recall fluctuates without a clear trend (0.251, 0.201, 0.287, and 0.211 across the four levels) and carries visibly larger dispersions, consistent with the higher optimization variance of on-policy methods. The two rule-based baselines are essentially flat, as expected from policies that do not observe the channel. One plausible reading is that stronger correlation makes the fading process more predictable, which a value-based agent can exploit more directly than a stochastic policy-gradient agent; we state this as a hypothesis rather than a conclusion, since the present grid cannot separate it from seed-level optimization noise.\n\n### B. Recall versus CSI Noise σ_est")

rep("This is the central robustness measurement of the paper: it quantifies how much mission-critical recall degrades when the transmitter's channel estimate deteriorates.",
    "This is the central robustness measurement of the paper: it quantifies how much mission-critical recall degrades when the transmitter's channel estimate deteriorates, now under the corrected reward.")

rep("**TABLE V. Recall@high versus σ_est (ρ = 0.85)**",
    "**TABLE V. Recall@high versus σ_est (in dB) (ρ = 0.85, corrected reward)**")
rep("| Method | σ_est = 0.0 | 0.6 | 1.2 | 2.0 (dB) |",
    "| Method | σ_est = 0.0 | σ_est = 0.6 | σ_est = 1.2 | σ_est = 2.0 |")

rep("### C. Bit–Recall Trade-off",
    "The CSI-noise sweep isolates robustness to estimation error. The Double-DQN recall degrades gracefully and roughly monotonically from 0.329 at σ_est = 0.0 dB to 0.267 at σ_est = 2.0 dB, whereas the PPO recall is non-monotonic — 0.183, 0.240, 0.287, and 0.236 — peaking at the intermediate noise level rather than at perfect CSI. The baselines are unchanged by construction. A tentative interpretation is that a small amount of observation noise regularizes the PPO policy against overconfident granularity choices, while larger noise eventually degrades its decisions; confirming this would require a finer σ_est grid and more seeds, which the checkpointed pipeline supports. The practical reading for deployment is that both learned agents retain 0.24–0.29 recall even at the highest noise level, so the correction is not fragile to CSI quality.\n\n### C. Bit–Recall Trade-off")

rep("Figure 1 plots the bit–recall trade-off", "Fig. 1 plots the bit–recall trade-off")
rep("Figure 2 shows Recall@high versus ρ", "Fig. 2 shows Recall@high versus ρ")

rep("**TABLE VI. Grid-mean performance summary (16 configurations × 3 seeds, greedy evaluation)**",
    "**TABLE VI. Grid-mean performance summary (16 configurations × 3 seeds, greedy evaluation, corrected reward)**")
rep("| Method | Recall@high | Semantic utility | Bits/step | Params | Latency (ms/step) |",
    "| Method | Recall@high | Semantic utility/step | Bits/step | Params | Latency (ms/step) |")

# ---------- VI-D ----------
rep("Table VI aggregates the full grid under the corrected reward. The headline finding is that the correction works: under the original utility-only reward both learned agents fail to deliver the mission metric (grid-mean Recall@high of 0.006 for PPO and 0.074 for Double-DQN versus 0.221 for the fixed policy and 0.346 for EqualGran — a factor of roughly 50 for PPO and 5 for DQN below EqualGran, consistent across all 16 configurations and not attributable to seed luck); after the recall-aware correction, PPO reaches 0.236 and Double-DQN 0.288, competitive with the parameter-free baselines. The diagnosis below explains why the original reward failed.",
    "Table VI aggregates the full grid under the corrected reward. The correction removes the zero-recall failure mode but does not make the learned agents winners on raw recall: under the uncorrected reward both agents were near zero (grid means 0.006 for PPO and 0.074 for Double-DQN, versus 0.221 for the fixed policy and 0.346 for EqualGran — a gap consistent across all 16 configurations and not attributable to seed luck), while under the corrected reward they recover to 0.236 and 0.288, and the equal-granularity baseline still attains the highest raw recall (0.346) at 288.0 bits per step. The diagnosis below explains why the original reward failed and how the correction removes the misalignment.")

rep("The reward optimizes weighted semantic utility, and under the present weights the marginal economics of granularity are decisive.",
    "Under the original weights of (9), the reward optimizes weighted semantic utility, and the marginal economics of granularity are decisive.")
rep("Upgrading from coarse (g = 1) to medium (g = 2) raises the weighted utility from 0.272 to 0.476 (+0.204) but raises the bit-cost penalty by 16 bits × λ_1 = 0.240, with smaller additional latency and energy penalties; the net per-region, per-step change is approximately −0.04.",
    "Upgrading from coarse (g = 1) to medium (g = 2) raises the weighted utility by 0.875 × (0.70 − 0.40) × sigmoid((10 − 5)/4) ≈ +0.204 (from 0.272 to 0.476) but raises the bit-cost penalty by (24 − 8) × λ_1 = 16 × 0.015 = 0.240, with smaller additional latency and energy penalties; the net per-region, per-step change is approximately −0.04.")

rep("PPO's grid-mean semantic utility (1.017) is *below* Double-DQN's (1.466), even though semantic utility is PPO's own training objective.",
    "Under the original reward, PPO's grid-mean semantic utility (1.017) is *below* Double-DQN's (1.466), even though semantic utility is PPO's own training objective.")

rep("a distinction that matters when interpreting the learned agents' equally flat but near-zero curves, which reflect persistent coarse transmission rather than channel-aware hedging.",
    "a distinction that matters when interpreting the learned agents' uncorrected near-zero curves, which reflected persistent coarse transmission rather than channel-aware hedging.")

rep("**Bit–recall trade-off.** Figure 1 places the four schemes on the cost–benefit plane. PPO occupies the low-bit, zero-recall corner (51.9 bits per step on average); EqualGran occupies the high-recall, high-bit corner (288 bits per step, 0.346 recall); the fixed policy sits between them (142.1 bits, 0.221 recall). Double-DQN is Pareto-dominated by the fixed policy at every σ_est level — it spends more bits for less recall — so the Pareto frontier is PPO → Fixed → EqualGran. Notably, the cheapest route to meaningful recall in this system is not learning at all but the fixed medium-granularity policy, which is Pareto-efficient and parameter-free.",
    "**Bit–recall trade-off.** Fig. 1 places the four schemes on the cost–benefit plane under the corrected reward. The equal-granularity baseline occupies the high-recall, high-bit corner (288.0 bits per step, recall 0.346), while the two learned agents cluster at roughly 40% of that bit cost with recall 0.24–0.29; the fixed policy (142.1 bits per step, recall 0.221) is dominated, since PPO achieves higher recall at fewer bits. The Pareto frontier therefore consists of the two learned-agent points and the EqualGran corner: on this plane the cheapest route to meaningful recall is the aligned learned policy, while the highest raw recall remains a parameter-free heuristic.")

rep("**Algorithm comparison and deployment cost.** The complexity measurements of Table III quantify what the learned agents cost without, in this configuration, repaying: PPO carries roughly one third of Double-DQN's trainable parameters (37,395 versus 109,248) yet about 17× higher per-step inference latency (2.329 versus 0.138 ms) due to five categorical heads and value computation. Under the original reward, neither agent surpasses the parameter-free baselines, so the honest engineering conclusion is negative for that reward design, not for policy-gradient methods in general; under the corrected reward the complexity cost is repaid by recovered recall.",
    "**Algorithm comparison and deployment cost.** The two learned agents also differ markedly in onboard cost (Table III): PPO carries roughly one third of Double-DQN's trainable parameters (37,395 versus 109,248) yet about 17× higher per-step inference latency (2.329 versus 0.138 ms) due to its five categorical heads and value computation. The corrected reward converts this overhead into recall within 0.06–0.11 of the best heuristic, whereas the uncorrected reward left the cost entirely unrepaid.")

rep_line("What closed the gap",
    "**How the correction removes the misalignment.** Three changes reverse the sign. First, λ_1 is reweighted from 0.015 to 0.008, reducing the bit penalty on the same upgrade to 0.128 so the utility gain dominates. Second, the recall-aware term λ_R Σ_i s_i P_recall(·) credits the policy directly for recovered high-priority content. Third, the high-priority action mask forbids the structurally recall-incapable levels g ∈ {0, 1}, so the policy can no longer settle into zero-recall transmission. Together they align the optimized objective with Recall@high.\n\n**Effect of the correction (Tables IV–VI).** The correction removes the zero-recall failure mode but does not make the learned agents winners on raw recall. Under the uncorrected reward both agents were near zero; under the corrected reward they recover to grid means of 0.236 (PPO) and 0.288 (Double-DQN), yet the equal-granularity baseline still attains the highest raw recall (0.346) at 288.0 bits per step. The learned agents' advantage is efficiency rather than superiority: at 116.2 and 118.5 bits per step, they approach the heuristic's recall at roughly 40% of its bit cost, as the bit–recall plane in Fig. 1 shows.")

rep("Third, and most consequentially for the present results, under the original reward the optimized objective is a weighted semantic-utility surrogate rather than recall; the negative benchmark outcome is a direct measurement of the resulting surrogate bias, and the marginal-reward analysis of this section explains it quantitatively. The corrected reward removes this bias, as the same analysis shows.",
    "Third, and most consequentially for the present results, the optimized objective remains a weighted semantic-utility-plus-recall surrogate rather than the mission metric itself; the uncorrected benchmark outcome is a direct measurement of the resulting surrogate bias, and the marginal-reward analysis of this section explains it quantitatively, while the corrected reward shows that the bias is removable but not eliminable by reweighting alone.")

# ---------- Conclusion / future work / nomenclature / new sections ----------
rep_line("Our key insight is that",
    "This paper reports a negative result together with its mechanistic explanation. In the factored formulation studied here, the binding constraint on mission-critical recall is not channel correlation, CSI noise, or the choice between policy-gradient and value-based learning. It is the alignment between the reward a learner is given and the metric the mission cares about.\n\nWe formulated joint semantic granularity allocation and UAV trajectory optimization for emergency imagery as a factored MDP under correlated Rayleigh fading, imperfect CSI, and a coupled energy budget, solved it with PPO, and benchmarked it against a Double-DQN baseline, a fixed policy, and an equal-granularity baseline under a strict multi-seed protocol over a 4×4 grid of channel correlation and CSI noise. We showed that a naive utility-only surrogate misaligns with the recall metric — under the original bit-cost weight, upgrading a high-priority region to recall-supporting granularity is economically irrational — and we corrected it with a recall-aware reward term, a reweighted cost, and a high-priority action mask.\n\nThe correction eliminated the zero-recall failure mode, but it did not crown the learned agents: the corrected PPO and Double-DQN agents reach grid-mean Recall@high of 0.236 and 0.288, while a parameter-free equal-granularity baseline still attains the highest raw recall (0.346) at 288.0 bits per step. The learned agents' genuine advantage is efficiency — they approach that recall at roughly 40% of the bit cost — and the diagnosis itself is the transferable contribution: aligning the optimized objective with the mission metric is a necessary condition for learned semantics-aware control, and it is checkable in advance through the marginal economics of the reward. The two learners also differ markedly in onboard deployment cost, quantified in Table III.")

rep_line("Future work proceeds along four directions",
    "Future work proceeds along four directions: (i) fitting the semantic utility and recall models with measured channel traces and real disaster aerial imagery; (ii) extending the relay to multiple cooperating UAVs; (iii) extending the trajectory design to three dimensions, including altitude optimization; and (iv) studying the recall-aware reward under a unified activation function to remove the tanh/ReLU confounding factor.")

rep("| γ, λ, ε | PPO discount factor, GAE parameter, clipping range |",
    "| γ, λ, ε | Discount factor (PPO and Double-DQN), GAE parameter, PPO clipping range |")

# insert Acknowledgment + Data availability before Nomenclature
rep("## Nomenclature",
    "## Acknowledgment\n\nThe authors would like to thank [Funder / Grant No. XXX] for supporting this work. [If no funding: This work was carried out without external funding.] During the preparation of this work the authors used [tool name] in order to improve the English language and readability of the manuscript. After using this tool, the authors reviewed and edited the content as needed and take full responsibility for the content of the published article.\n\n## Data and Code Availability\n\nThe simulation environment, training and evaluation code, and the full multi-seed result tables (16 configurations × 3 seeds, including the uncorrected- and corrected-reward runs) are available at [repository URL, e.g., a GitHub or Code Ocean repository]. All model checkpoints written every 50 training episodes are preserved, so every reported number can be regenerated without retraining. The software stack is Python 3.13.14, PyTorch 2.14.0 (CPU build), Gymnasium 1.4.0, and NumPy 2.5.2.\n\n## Nomenclature")

open(mp, "w", encoding="utf-8").write(text)
print("all md phases ok")

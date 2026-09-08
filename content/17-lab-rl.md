---
id: lab-rl
title: 实验 01：用成熟 PPO 库跑通闭环
summary: 用 FrozenLake 理解训练、评测、随机种子与日志，不需要 GPU 或 API Key。
stage: FOUNDATION
track: 实验与维护
order: 18
minutes: 30
updated: '2026-09-08'
review: 实验指南
tags: [lab, PPO, CPU, reproducibility]
sources: [gymnasium, sb3, ppo]
prerequisites: [ppo]
---
## 目标与限制

先在离散环境上比较随机策略与 PPO，掌握最小实验协议。FrozenLake 不含语言工具调用，因此这个实验验证的是 RL 流程，不能证明 Agentic RL 能力。使用非滑动地图降低首次运行难度，之后再增加随机性。

## 环境准备

建议 Python 3.11 的独立虚拟环境；依赖与脚本位于仓库 `experiments/`。CPU 即可，完整运行时间取决于机器。安装 PyTorch 依赖可能需要额外下载。

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r experiments/requirements.txt
python experiments/train_ppo.py --steps 30000 --seed 42
```

脚本使用 SB3 的 PPO，不手写训练引擎。训练环境与评测环境独立；评测种子固定；报告随机基线与训练后策略的成功计数。输出 JSON 是本地产物，不自动写入知识结论。

## 应观察什么

首次运行不承诺一定学会。若成功率低，先检查训练步数、稀疏奖励、熵与探索，再改超参数。一次好种子不能代表稳定性，至少使用 3 个训练种子，并保存每次原始计数。

## 可证伪的实验问题

固定总训练步数，对比探索参数或启用 slippery 地图，成功率和种子方差怎样变化？如果只改评测地图却没声明分布变化，就不能公平比较分数。

## 完成标准

提交实验卡：假设、版本、超参数、训练种子、评测任务、成功数/总数、成本、失败例子与结论边界。运行记录与“推荐参数”分开存放，失败也保留。接着做 [工具轨迹评测](/notes/lab-agent)。

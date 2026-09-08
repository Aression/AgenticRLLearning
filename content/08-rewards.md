---
id: rewards
title: 奖励、验证器与信用分配
summary: 区分结果奖励和过程信号，避免把可优化的代理指标误当真实目标。
stage: SYSTEMS
track: 训练算法
order: 9
minutes: 20
updated: '2026-09-08'
review: 综合笔记
tags: [reward, verifier, credit assignment]
sources: [deepseek-math, gigpo, lilian-reward]
prerequisites: [mdp, environments]
---
## 奖励来源

结果奖励判断最终成功，例如隐藏测试通过；过程奖励评价中间步骤；偏好模型从比较数据学习评分；规则验证器执行可计算检查。程序验证器能降低人工标注成本，但它检查的是被编码的条件，而不是所有现实正确性。

## 多目标例子

可将目标写成 $R=\mathbb 1[success]-\alpha\cdot calls-\beta\cdot cost$。这里的权重只是设计参数，必须结合独立成功率与成本报告。过高的调用惩罚可能鼓励提前放弃；格式奖励过强则可能学会漂亮地失败。

## 稀疏奖励为什么难

20 步后收到一次失败，无法直接知道是第 2 步检索错了还是第 19 步编辑错了。把终局奖励广播到所有 token 是一个估计方案，不是因果解释。细粒度 critic、子目标和同状态分组都试图提高归因信息，但各有假设与开销。

## Reward shaping 的边界

理论上特定形式的 potential-based shaping 在对应假设下可保留最优策略，任意添加“多思考加分”“工具调用加分”没有这种保证。过程监督还面临步骤标注成本、评价偏差和模型利用评分漏洞的问题。

## 验证器测试

为正确答案、错误答案、格式投机、空输出、超时和修改测试文件分别准备用例。训练验证器和最终评测 oracle 尽可能分离；评测集不能作为不断调 reward 的训练反馈。

## 自测

高代码覆盖率不是功能正确；通过公开测试不是通过隐藏测试；高模型裁判分数不是用户价值的证明。下一步比较 [RLHF 与偏好优化](/notes/preferences) 和 [GRPO](/notes/grpo)。

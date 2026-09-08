"""Small CPU baseline. Every run writes a seed-specific JSON record."""
import argparse
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=30_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--slippery", action="store_true")
    args = parser.parse_args()
    env = gym.make("FrozenLake-v1", is_slippery=args.slippery)
    eval_env = gym.make("FrozenLake-v1", is_slippery=args.slippery)
    model = PPO("MlpPolicy", env, seed=args.seed, verbose=0)
    started = datetime.now(timezone.utc)
    model.learn(total_timesteps=args.steps)
    mean_reward, std_reward = evaluate_policy(model, eval_env, n_eval_episodes=100, deterministic=True)
    record = {
        "experiment": "ppo-frozenlake",
        "startedAt": started.isoformat(),
        "finishedAt": datetime.now(timezone.utc).isoformat(),
        "steps": args.steps,
        "seed": args.seed,
        "slippery": args.slippery,
        "meanReward": float(mean_reward),
        "stdReward": float(std_reward),
        "python": platform.python_version(),
        "note": "This baseline tests PPO plumbing, not Agentic RL capability.",
    }
    Path("experiments/runs").mkdir(parents=True, exist_ok=True)
    output = Path("experiments/runs") / f"ppo-frozenlake-seed-{args.seed}.json"
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()

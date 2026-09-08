"""Deterministic tool trajectory and verifier; no network or model calls."""
from dataclasses import dataclass
import json


CATALOG = {"red pen": 3, "blue notebook": 7, "adapter": 12}


@dataclass
class ToolEnv:
    calls: int = 0
    total: int = 0
    done: bool = False

    def step(self, action: dict) -> tuple[dict, int, bool]:
        self.calls += 1
        if self.calls > 6:
            return {"error": "budget_exceeded"}, -1, True
        tool = action.get("tool")
        if tool == "lookup":
            item = action.get("args", {}).get("item")
            if item not in CATALOG:
                return {"error": "unknown_item"}, -1, True
            return {"item": item, "price": CATALOG[item]}, 0, False
        if tool == "add":
            values = action.get("args", {}).get("values", [])
            if not values or any(not isinstance(value, int) for value in values):
                return {"error": "invalid_values"}, -1, True
            self.total = sum(values)
            return {"total": self.total}, 0, False
        if tool == "finish":
            result = action.get("args", {}).get("result")
            self.done = True
            return {"submitted": result}, int(result == self.total == 10), True
        return {"error": "tool_not_allowed"}, -1, True


def run(actions: list[dict]) -> dict:
    env, trace = ToolEnv(), []
    for step, action in enumerate(actions):
        observation, reward, done = env.step(action)
        trace.append({"step": step, "action": action, "observation": observation, "reward": reward, "terminated": done})
        if done:
            break
    return {"success": bool(trace and trace[-1]["reward"] == 1), "trace": trace}


def main():
    examples = {
        "valid": [{"tool": "lookup", "args": {"item": "red pen"}}, {"tool": "lookup", "args": {"item": "blue notebook"}}, {"tool": "add", "args": {"values": [3, 7]}}, {"tool": "finish", "args": {"result": 10}}],
        "invalid": [{"tool": "delete_file", "args": {}}, {"tool": "finish", "args": {"result": 10}}],
    }
    print(json.dumps({name: run(actions) for name, actions in examples.items()}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

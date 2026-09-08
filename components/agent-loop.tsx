"use client";
import { useEffect, useRef, useState } from "react";
const steps = [
  { label: "POLICY", detail: "策略 π(a | h)：从任务历史选择工具动作。", color: "#67ddcb" },
  { label: "ENVIRONMENT", detail: "环境执行动作，返回新的观测与状态变化。", color: "#f3c578" },
  { label: "TRAJECTORY", detail: "轨迹 τ：记录动作、观测、回报和终止条件。", color: "#efa3b5" },
  { label: "LEARNER", detail: "训练器以回报更新参数，再同步给执行策略。", color: "#bec7d0" },
];
export function AgentLoop() {
  const canvas = useRef<HTMLCanvasElement>(null);
  const [active, setActive] = useState(0);
  useEffect(() => {
    const element = canvas.current;
    if (!element) return;
    const draw = () => {
      const width = element.clientWidth, height = element.clientHeight, scale = window.devicePixelRatio || 1;
      element.width = width * scale; element.height = height * scale;
      const ctx = element.getContext("2d"); if (!ctx) return;
      ctx.scale(scale, scale); ctx.fillStyle = "#101214"; ctx.fillRect(0, 0, width, height);
      ctx.fillStyle = "#2b2e31";
      for (let x = 12; x < width; x += 18) for (let y = 12; y < height; y += 18) ctx.fillRect(x, y, 1, 1);
      const points = [{ x: width * .23, y: 52 }, { x: width * .76, y: 52 }, { x: width * .76, y: 145 }, { x: width * .23, y: 145 }];
      points.forEach((from, i) => {
        const to = points[(i + 1) % points.length], angle = Math.atan2(to.y - from.y, to.x - from.x);
        const x = to.x - Math.cos(angle) * 43, y = to.y - Math.sin(angle) * 23;
        ctx.strokeStyle = i === active ? steps[i].color : "#42474c"; ctx.lineWidth = 1;
        ctx.beginPath(); ctx.moveTo(from.x, from.y); ctx.lineTo(x, y); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(x - 6 * Math.cos(angle - .5), y - 6 * Math.sin(angle - .5)); ctx.lineTo(x, y); ctx.lineTo(x - 6 * Math.cos(angle + .5), y - 6 * Math.sin(angle + .5)); ctx.stroke();
      });
      points.forEach((point, i) => {
        ctx.fillStyle = "#101214"; ctx.fillRect(point.x - 49, point.y - 20, 98, 40);
        ctx.strokeStyle = i === active ? steps[i].color : "#42474c"; ctx.strokeRect(point.x - 49, point.y - 20, 98, 40);
        ctx.fillStyle = steps[i].color; ctx.font = '10px Consolas, monospace'; ctx.textAlign = "center"; ctx.fillText(steps[i].label, point.x, point.y + 4);
      });
      ctx.fillStyle = "#9a9da1"; ctx.font = '9px Consolas, monospace'; ctx.fillText("act / observe / optimize", width / 2, 101);
    };
    const resize = new ResizeObserver(draw); resize.observe(element); draw(); return () => resize.disconnect();
  }, [active]);
  return <div className="loop-tool"><canvas ref={canvas} role="img" aria-label="策略、环境、轨迹、训练器组成的 Agent RL 闭环" /><div className="loop-controls" role="group" aria-label="闭环阶段">{steps.map((step, i) => <button key={step.label} title={step.label} onClick={() => setActive(i)} aria-pressed={active === i}>{String(i + 1).padStart(2, "0")}</button>)}</div><p>{steps[active].detail}</p></div>;
}

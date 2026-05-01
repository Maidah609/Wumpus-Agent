from __future__ import annotations

import random
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from agent import LogicAgent
from world import WorldConfig, WumpusWorld


ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")

world = WumpusWorld(WorldConfig())
agent = LogicAgent(world)


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/api/state")
def get_state():
    return jsonify(agent.state_payload())


@app.post("/api/reset")
def reset_world():
    data = request.get_json(silent=True) or {}
    rows = int(data.get("rows", 4))
    cols = int(data.get("cols", 4))
    pit_probability = float(data.get("pitProbability", 0.2))
    seed = data.get("seed")

    rows = max(2, min(rows, 12))
    cols = max(2, min(cols, 12))
    pit_probability = max(0.05, min(pit_probability, 0.45))
    if seed is not None and str(seed).strip() != "":
        random.seed(int(seed))

    global world, agent
    world = WumpusWorld(WorldConfig(rows=rows, cols=cols, pit_probability=pit_probability))
    agent = LogicAgent(world)
    return jsonify(agent.state_payload())


@app.post("/api/step")
def step():
    result = agent.step()
    payload = agent.state_payload()
    payload["last_action"] = result["status"]
    return jsonify(payload)


@app.post("/api/auto")
def auto():
    data = request.get_json(silent=True) or {}
    max_steps = int(data.get("maxSteps", 50))
    max_steps = max(1, min(max_steps, 300))
    run_info = agent.auto_run(max_steps=max_steps)
    payload = agent.state_payload()
    payload["last_action"] = run_info["status"]
    payload["steps_executed"] = run_info["steps_executed"]
    return jsonify(payload)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

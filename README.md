# Dynamic Wumpus Logic Agent (Web App)

This project implements a Knowledge-Based Agent for a dynamic Wumpus World grid.
The agent receives percepts (`Breeze`, `Stench`), updates a propositional KB, and uses
Resolution Refutation to decide whether an unvisited cell is safe.

## Features

- Dynamic grid size (`Rows x Cols`)
- Random hazards each episode (pits + one wumpus)
- Percept-driven logic updates to KB
- Resolution-based `ASK` before movement
- Web GUI with:
  - Green = safe
  - Gray = unknown
  - Red = deduced hazard
  - Yellow = agent
- Real-time metrics:
  - Total inference steps
  - Current percepts
  - visited cells

## Project Structure

```text
assignment3/
  backend/
    app.py
    agent.py
    kb.py
    world.py
  frontend/
    index.html
    style.css
    script.js
  requirements.txt
  README.md
```

## Run Locally

1. Open terminal in project root.
2. Install dependencies:
   - `python -m pip install -r requirements.txt`
3. Start server:
   - `python backend/app.py`
4. Open browser:
   - [http://127.0.0.1:5000](http://127.0.0.1:5000)

## How It Works

1. Agent starts at `(0,0)` with known safety facts.
2. At each step, it senses local percepts:
   - `B(r,c)` if adjacent to any pit
   - `S(r,c)` if adjacent to wumpus
3. The KB stores CNF-compatible clauses from percept equivalences.
4. Before entering a new neighboring cell `x`, the agent asks KB:
   - `entails(~P_x)` and `entails(~W_x)` using resolution refutation.
5. If both are proven, the cell is safe and can be selected.


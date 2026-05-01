# AI Assignment 6 Report - Dynamic Wumpus Logic Agent

## Student Information
- Name: [Your Name]
- Roll Number: [XXF-YYYY]
- Course: Artificial Intelligence
- Assignment: A6 - Coding Project

## Required Links (Put on First Page)
- GitHub Repository: [Paste URL]
- Live Deployment URL: [Paste URL]
- LinkedIn Post URL: [Paste URL]

## 1) Project Objective
The goal is to implement a dynamic pathfinding Knowledge-Based Agent for the Wumpus World.
The agent does not know hazard locations initially. It receives percepts (`Breeze`, `Stench`)
from the environment and uses Propositional Logic with Resolution Refutation to infer safe cells.

## 2) Environment Design
- Grid Size: User configurable (`rows x cols`)
- Hazards per Episode:
  - Multiple random pits
  - One random wumpus
- Percepts:
  - Breeze if adjacent to any pit
  - Stench if adjacent to wumpus

## 3) Knowledge Base Representation
The KB is stored as CNF clauses using literals like:
- `P_r_c` -> pit in cell `(r, c)`
- `W_r_c` -> wumpus in cell `(r, c)`
- `B_r_c` -> breeze at `(r, c)`
- `S_r_c` -> stench at `(r, c)`

When the agent observes a cell, it adds percept equivalence rules:
- `B_r_c <-> (OR of adjacent pits)`
- `S_r_c <-> (OR of adjacent wumpus possibilities)`

For absent percepts, adjacent hazards are negated.

## 4) CNF Conversion Summary
For `X <-> (A v B v C)`:
- `(¬X v A v B v C)`
- `(X v ¬A)`
- `(X v ¬B)`
- `(X v ¬C)`

This transformation is used for both breeze and stench rules.

## 5) Resolution Refutation Loop
To prove query `Q`:
1. Add `¬Q` to clause set.
2. Repeatedly resolve clause pairs.
3. If empty clause `{}` is derived -> contradiction found -> `Q` is entailed.
4. If no new clause can be produced -> `Q` not entailed.

Safety query for candidate cell `(r, c)`:
- prove `¬P_r_c`
- prove `¬W_r_c`
- move only if both are entailed.

## 6) Agent Behavior
1. Start at `(0,0)` and mark safe.
2. Read percepts at current location.
3. Update KB with CNF clauses.
4. Ask KB for safety of unvisited adjacent cells.
5. Move to a cell proven safe; otherwise stop when no safe move exists.

## 7) Web Interface and Metrics
The GUI shows:
- Safe cells (Green)
- Unknown cells (Gray)
- Confirmed hazards (Red)
- Agent location (Yellow)

Dashboard metrics:
- Current percepts
- Total inference steps
- Visited cells and move count

## 8) Testing Performed
- Manual reset with different grid sizes
- Manual stepping
- Auto-run for fixed step count
- API verification:
  - `GET /api/state`
  - `POST /api/reset`
  - `POST /api/step`
  - `POST /api/auto`

## 9) Challenges and Solutions
- Challenge: Efficient logic inference with growing clauses.
- Solution: Keep practical inference checks focused around relevant local cells and decision-time safety queries.
- Challenge: Mapping logic states to visual states.
- Solution: Dedicated grid status model (`unknown/safe/visited/hazard/agent`) returned by backend.

## 10) Conclusion
The project successfully demonstrates a dynamic knowledge-based agent using propositional logic and
resolution refutation in an interactive web application. It satisfies the assignment requirement for
dynamic environment setup, logical inference, and real-time visualization.

## 11) Viva Preparation Checklist
- Change grid size and re-run in front of examiner.
- Explain one full safety proof example (`¬P` and `¬W` checks).
- Show where CNF clauses are generated in code.
- Demonstrate that hazards are randomized each reset.

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from kb import KnowledgeBase, breeze_var, pit_var, stench_var, wumpus_var
from world import WumpusWorld


Cell = Tuple[int, int]


@dataclass
class AgentState:
    position: Cell = (0, 0)
    visited: Set[Cell] = field(default_factory=lambda: {(0, 0)})
    safe_cells: Set[Cell] = field(default_factory=lambda: {(0, 0)})
    confirmed_pits: Set[Cell] = field(default_factory=set)
    confirmed_wumpus: Set[Cell] = field(default_factory=set)
    alive: bool = True
    won: bool = False
    last_percepts: Dict[str, bool] = field(default_factory=dict)
    move_count: int = 0
    decision_log: List[str] = field(default_factory=list)


class LogicAgent:
    def __init__(self, world: WumpusWorld):
        self.world = world
        self.kb = KnowledgeBase()
        self.state = AgentState()
        self._seed_start_cell_knowledge()
        self.observe_current_cell()

    def reset(self) -> None:
        self.kb = KnowledgeBase()
        self.state = AgentState()
        self._seed_start_cell_knowledge()
        self.observe_current_cell()

    def _seed_start_cell_knowledge(self) -> None:
        # Start cell is guaranteed safe.
        self.kb.add_clause([f"~{pit_var((0, 0))}"])
        self.kb.add_clause([f"~{wumpus_var((0, 0))}"])
        self._log("Initialized KB with start cell safety facts.")

    def _log(self, message: str) -> None:
        self.state.decision_log.append(message)
        # Keep log concise for UI.
        if len(self.state.decision_log) > 30:
            self.state.decision_log = self.state.decision_log[-30:]

    def observe_current_cell(self) -> None:
        cell = self.state.position
        percepts = self.world.get_percepts(cell)
        self.state.last_percepts = percepts
        self._log(
            f"Observed {cell}: breeze={percepts['breeze']}, stench={percepts['stench']}."
        )

        neighbors = self.world.neighbors(cell)
        pit_neighbors = [pit_var(n) for n in neighbors]
        wumpus_neighbors = [wumpus_var(n) for n in neighbors]

        self.kb.tell_percept_equivalence(
            breeze_var(cell),
            pit_neighbors,
            percepts["breeze"],
        )
        self.kb.tell_percept_equivalence(
            stench_var(cell),
            wumpus_neighbors,
            percepts["stench"],
        )

        focus_cells = {cell, *neighbors}
        self._refresh_deductions(focus_cells)

    def _refresh_deductions(self, candidate_cells: Set[Cell]) -> None:
        for cell in candidate_cells:
            pit_confirmed, _ = self.kb.entails(pit_var(cell))
            wumpus_confirmed, _ = self.kb.entails(wumpus_var(cell))
            pit_absent, _ = self.kb.entails(f"~{pit_var(cell)}")
            wumpus_absent, _ = self.kb.entails(f"~{wumpus_var(cell)}")

            if pit_confirmed:
                self.state.confirmed_pits.add(cell)
            if wumpus_confirmed:
                self.state.confirmed_wumpus.add(cell)
            if pit_absent and wumpus_absent:
                self.state.safe_cells.add(cell)

    def choose_next_cell(self) -> Cell | None:
        neighbors = self.world.neighbors(self.state.position)
        unvisited_neighbors = [n for n in neighbors if n not in self.state.visited]

        safe_candidates: List[Cell] = []
        evaluations = []
        for cell in unvisited_neighbors:
            safe, steps = self.kb.ask_safe(cell)
            evaluations.append((cell, safe, steps))
            if safe:
                safe_candidates.append(cell)
        if evaluations:
            formatted = ", ".join(
                [f"{cell}:safe={safe},steps={steps}" for cell, safe, steps in evaluations]
            )
            self._log(f"Evaluated neighbors -> {formatted}")

        if safe_candidates:
            chosen = random.choice(safe_candidates)
            self._log(f"Selected safe unvisited cell {chosen}.")
            return chosen

        # Fall back to known-safe visited cell to continue exploring from there.
        visited_safe_neighbors = [n for n in neighbors if n in self.state.safe_cells]
        if visited_safe_neighbors:
            chosen = random.choice(visited_safe_neighbors)
            self._log(f"No new provably safe cell. Backtracking to visited safe cell {chosen}.")
            return chosen

        self._log("No safe next move could be proven.")
        return None

    def step(self) -> Dict[str, str]:
        if not self.state.alive or self.state.won:
            return {"status": "finished"}

        next_cell = self.choose_next_cell()
        if next_cell is None:
            self.state.won = True
            self._log("Episode completed: no further safe move available.")
            return {"status": "no-safe-move"}

        self.state.position = next_cell
        self.state.visited.add(next_cell)
        self.state.move_count += 1

        if self.world.is_pit(next_cell) or self.world.is_wumpus(next_cell):
            self.state.alive = False
            self._log(f"Moved to {next_cell} and hit a hazard. Agent died.")
            return {"status": "dead"}

        self.state.safe_cells.add(next_cell)
        self.observe_current_cell()
        self._log(f"Moved safely to {next_cell}.")
        return {"status": "moved"}

    def auto_run(self, max_steps: int = 100) -> Dict[str, int | str]:
        status = "moved"
        steps = 0
        while steps < max_steps and self.state.alive and not self.state.won:
            result = self.step()
            status = str(result["status"])
            steps += 1
            if status in {"dead", "no-safe-move"}:
                break
        return {"status": status, "steps_executed": steps}

    def grid_data(self) -> List[List[str]]:
        rows, cols = self.world.config.rows, self.world.config.cols
        grid = [["unknown" for _ in range(cols)] for _ in range(rows)]

        for cell in self.state.safe_cells:
            r, c = cell
            grid[r][c] = "safe"
        for cell in self.state.confirmed_pits | self.state.confirmed_wumpus:
            r, c = cell
            grid[r][c] = "hazard"
        for cell in self.state.visited:
            r, c = cell
            if grid[r][c] != "hazard":
                grid[r][c] = "visited"

        ar, ac = self.state.position
        grid[ar][ac] = "agent"
        return grid

    def truth_grid_data(self) -> List[List[str]]:
        rows, cols = self.world.config.rows, self.world.config.cols
        truth = [["empty" for _ in range(cols)] for _ in range(rows)]
        for cell in self.world.pits:
            r, c = cell
            truth[r][c] = "pit"
        if self.world.wumpus is not None:
            wr, wc = self.world.wumpus
            truth[wr][wc] = "wumpus"
        return truth

    def state_payload(self) -> Dict:
        total_cells = self.world.config.rows * self.world.config.cols
        unknown_count = total_cells - len(self.state.safe_cells) - len(
            self.state.confirmed_pits | self.state.confirmed_wumpus
        )
        return {
            "rows": self.world.config.rows,
            "cols": self.world.config.cols,
            "position": self.state.position,
            "alive": self.state.alive,
            "won": self.state.won,
            "visited_count": len(self.state.visited),
            "move_count": self.state.move_count,
            "percepts": self.state.last_percepts,
            "inference_steps": self.kb.total_inference_steps,
            "grid": self.grid_data(),
            "truth_grid": self.truth_grid_data(),
            "confirmed_pits": sorted(list(self.state.confirmed_pits)),
            "confirmed_wumpus": sorted(list(self.state.confirmed_wumpus)),
            "decision_log": self.state.decision_log,
            "safe_count": len(self.state.safe_cells),
            "unknown_count": max(0, unknown_count),
        }

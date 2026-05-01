import random
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple


Cell = Tuple[int, int]


@dataclass
class WorldConfig:
    rows: int = 4
    cols: int = 4
    pit_probability: float = 0.2


class WumpusWorld:
    def __init__(self, config: WorldConfig):
        self.config = config
        self.start: Cell = (0, 0)
        self.pits: Set[Cell] = set()
        self.wumpus: Cell | None = None
        self.reset()

    def reset(self) -> None:
        self.pits.clear()
        self.wumpus = None
        cells = [
            (r, c)
            for r in range(self.config.rows)
            for c in range(self.config.cols)
            if (r, c) != self.start
        ]
        for cell in cells:
            if random.random() < self.config.pit_probability:
                self.pits.add(cell)
        if cells:
            self.wumpus = random.choice(cells)
            if self.wumpus in self.pits:
                self.pits.remove(self.wumpus)

    def in_bounds(self, cell: Cell) -> bool:
        r, c = cell
        return 0 <= r < self.config.rows and 0 <= c < self.config.cols

    def neighbors(self, cell: Cell) -> List[Cell]:
        r, c = cell
        candidates = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
        return [n for n in candidates if self.in_bounds(n)]

    def get_percepts(self, cell: Cell) -> Dict[str, bool]:
        neighbors = self.neighbors(cell)
        breeze = any(n in self.pits for n in neighbors)
        stench = self.wumpus in neighbors if self.wumpus is not None else False
        return {"breeze": breeze, "stench": stench}

    def is_pit(self, cell: Cell) -> bool:
        return cell in self.pits

    def is_wumpus(self, cell: Cell) -> bool:
        return self.wumpus == cell

from __future__ import annotations

from typing import Iterable, List, Set, Tuple


Clause = frozenset[str]


def negate(literal: str) -> str:
    return literal[1:] if literal.startswith("~") else f"~{literal}"


def pit_var(cell: Tuple[int, int]) -> str:
    return f"P_{cell[0]}_{cell[1]}"


def wumpus_var(cell: Tuple[int, int]) -> str:
    return f"W_{cell[0]}_{cell[1]}"


def breeze_var(cell: Tuple[int, int]) -> str:
    return f"B_{cell[0]}_{cell[1]}"


def stench_var(cell: Tuple[int, int]) -> str:
    return f"S_{cell[0]}_{cell[1]}"


class KnowledgeBase:
    def __init__(self):
        self.clauses: Set[Clause] = set()
        self.total_inference_steps = 0
        self._version = 0
        self._entailment_cache: dict[tuple[int, str], tuple[bool, int]] = {}

    def add_clause(self, literals: Iterable[str]) -> None:
        clause = frozenset(literals)
        if clause not in self.clauses:
            self.clauses.add(clause)
            self._version += 1
            self._entailment_cache.clear()

    def tell_percept_equivalence(
        self,
        source_var: str,
        neighbor_hazard_vars: List[str],
        is_present: bool,
    ) -> None:
        if is_present:
            self.add_clause([source_var])
            # source_var => OR(neighbor hazards)
            self.add_clause([negate(source_var), *neighbor_hazard_vars])
            # Each hazard implies the percept.
            for hazard in neighbor_hazard_vars:
                self.add_clause([source_var, negate(hazard)])
        else:
            self.add_clause([negate(source_var)])
            # If percept is absent, every adjacent hazard is false.
            for hazard in neighbor_hazard_vars:
                self.add_clause([negate(hazard)])

    def _resolve_pair(self, c1: Clause, c2: Clause) -> Set[Clause]:
        resolvents: Set[Clause] = set()
        for literal in c1:
            comp = negate(literal)
            if comp in c2:
                merged = set(c1.union(c2))
                merged.discard(literal)
                merged.discard(comp)
                # Skip tautological resolvents.
                if any(negate(x) in merged for x in merged):
                    continue
                resolvents.add(frozenset(merged))
        return resolvents

    def resolution_refutation(self, query: str) -> Tuple[bool, int]:
        max_pair_steps = 30000
        max_clause_count = 4000

        # To prove query, add negation(query) and derive contradiction.
        clauses = set(self.clauses)
        clauses.add(frozenset([negate(query)]))
        steps = 0

        while True:
            new: Set[Clause] = set()
            clause_list = list(clauses)
            n = len(clause_list)
            for i in range(n):
                for j in range(i + 1, n):
                    steps += 1
                    if steps >= max_pair_steps:
                        self.total_inference_steps += steps
                        return False, steps
                    resolvents = self._resolve_pair(clause_list[i], clause_list[j])
                    if frozenset() in resolvents:
                        self.total_inference_steps += steps
                        return True, steps
                    new |= resolvents
            if new.issubset(clauses):
                self.total_inference_steps += steps
                return False, steps
            clauses |= new
            if len(clauses) >= max_clause_count:
                self.total_inference_steps += steps
                return False, steps

    def entails(self, literal: str) -> Tuple[bool, int]:
        # Fast path: unit clause already known.
        if frozenset([literal]) in self.clauses:
            return True, 0

        key = (self._version, literal)
        if key in self._entailment_cache:
            return self._entailment_cache[key]

        result = self.resolution_refutation(literal)
        self._entailment_cache[key] = result
        return result

    def ask_safe(self, cell: Tuple[int, int]) -> Tuple[bool, int]:
        pit_safe, pit_steps = self.entails(negate(pit_var(cell)))
        wumpus_safe, wumpus_steps = self.entails(negate(wumpus_var(cell)))
        return pit_safe and wumpus_safe, pit_steps + wumpus_steps

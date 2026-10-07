"""Domain models used by the optimization algorithms."""

from __future__ import annotations

from dataclasses import dataclass

from .type_chart import TYPE_NAMES


VALID_DEFENSIVE_MULTIPLIERS = frozenset({0.0, 0.25, 0.5, 1.0, 2.0, 4.0})


@dataclass(frozen=True, slots=True)
class Pokemon:
    """A Pokemon and its precomputed response to all 18 attacking types.

    The order of ``defensive_vector`` always matches ``TYPE_NAMES``. Keeping
    this calculation outside the optimization loop makes repeated team
    evaluation inexpensive.
    """

    id: int
    name: str
    api_name: str
    type1: str
    type2: str | None
    defensive_vector: tuple[float, ...]

    def __post_init__(self) -> None:
        if self.id <= 0:
            raise ValueError("Pokemon id must be positive")
        if not self.name.strip() or not self.api_name.strip():
            raise ValueError("Pokemon names cannot be empty")
        if self.type1 not in TYPE_NAMES:
            raise ValueError(f"Unknown primary type: {self.type1}")
        if self.type2 is not None and self.type2 not in TYPE_NAMES:
            raise ValueError(f"Unknown secondary type: {self.type2}")
        if self.type2 == self.type1:
            raise ValueError("Primary and secondary type must differ")
        if len(self.defensive_vector) != len(TYPE_NAMES):
            raise ValueError(
                f"Defensive vector must have {len(TYPE_NAMES)} values"
            )
        invalid = set(self.defensive_vector) - VALID_DEFENSIVE_MULTIPLIERS
        if invalid:
            raise ValueError(f"Invalid defensive multipliers: {sorted(invalid)}")


"""Type-chart constants and defensive effectiveness calculations."""

from __future__ import annotations

from collections.abc import Mapping


TYPE_NAMES = (
    "Normal",
    "Fire",
    "Water",
    "Electric",
    "Grass",
    "Ice",
    "Fighting",
    "Poison",
    "Ground",
    "Flying",
    "Psychic",
    "Bug",
    "Rock",
    "Ghost",
    "Dragon",
    "Dark",
    "Steel",
    "Fairy",
)

TypeChart = Mapping[str, Mapping[str, float]]


def defensive_multiplier(
    chart: TypeChart,
    attack_type: str,
    type1: str,
    type2: str | None = None,
) -> float:
    """Return an attack's multiplier against a single- or dual-type defender."""
    if attack_type not in TYPE_NAMES:
        raise ValueError(f"Unknown attacking type: {attack_type}")
    if type1 not in TYPE_NAMES:
        raise ValueError(f"Unknown primary defending type: {type1}")
    if type2 is not None and type2 not in TYPE_NAMES:
        raise ValueError(f"Unknown secondary defending type: {type2}")
    if type2 == type1:
        raise ValueError("Primary and secondary defending type must differ")

    multiplier = chart[attack_type][type1]
    if type2 is not None:
        multiplier *= chart[attack_type][type2]
    return multiplier


def build_defensive_vector(
    chart: TypeChart, type1: str, type2: str | None = None
) -> tuple[float, ...]:
    """Precompute multipliers for attacks in canonical ``TYPE_NAMES`` order."""
    return tuple(
        defensive_multiplier(chart, attack_type, type1, type2)
        for attack_type in TYPE_NAMES
    )


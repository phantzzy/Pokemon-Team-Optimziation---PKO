"""Loading and validation for fixed optimization problem instances."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .data_loader import load_pokemon
from .evaluation import TEAM_SIZE
from .models import Pokemon


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INSTANCES_DIR = PROJECT_ROOT / "instances"


@dataclass(frozen=True, slots=True)
class ProblemInstance:
    """A named, fixed subset of candidate Pokemon."""

    name: str
    candidates: tuple[Pokemon, ...]

    @property
    def n(self) -> int:
        return len(self.candidates)


def load_instance(
    path: str | Path,
    dataset: Sequence[Pokemon] | None = None,
) -> ProblemInstance:
    """Load an instance and resolve its names against the local dataset."""
    resolved_path = Path(path)
    try:
        with resolved_path.open(encoding="utf-8") as file:
            raw_instance = json.load(file)
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Instance file not found: {resolved_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {resolved_path}: {error}") from error

    if not isinstance(raw_instance, dict):
        raise ValueError("Instance must be a JSON object")
    if set(raw_instance) != {"name", "pokemon"}:
        raise ValueError("Instance must contain exactly 'name' and 'pokemon'")
    name = raw_instance["name"]
    pokemon_names = raw_instance["pokemon"]
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Instance name must be a non-empty string")
    if not isinstance(pokemon_names, list) or any(
        not isinstance(item, str) for item in pokemon_names
    ):
        raise ValueError("Instance pokemon must be a list of names")
    if len(pokemon_names) < TEAM_SIZE:
        raise ValueError(f"Instance must contain at least {TEAM_SIZE} Pokemon")
    if len(pokemon_names) != len(set(pokemon_names)):
        raise ValueError("Instance Pokemon names must be unique")

    effective_dataset = tuple(dataset) if dataset is not None else load_pokemon()
    pokemon_by_name = {pokemon.name: pokemon for pokemon in effective_dataset}
    if len(pokemon_by_name) != len(effective_dataset):
        raise ValueError("Dataset Pokemon names must be unique")
    missing = [name for name in pokemon_names if name not in pokemon_by_name]
    if missing:
        raise ValueError(f"Instance contains unknown Pokemon: {missing}")

    return ProblemInstance(
        name=name,
        candidates=tuple(pokemon_by_name[item] for item in pokemon_names),
    )


def predefined_instance_paths() -> tuple[Path, ...]:
    """Return the five predefined instance paths from smallest to largest."""
    names = ("small_12", "medium_20", "medium_30", "large_50", "xlarge_100")
    return tuple(INSTANCES_DIR / f"{name}.json" for name in names)


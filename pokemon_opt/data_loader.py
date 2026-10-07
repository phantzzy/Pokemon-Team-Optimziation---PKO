"""Validated loaders for the project's local JSON data snapshot."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Pokemon
from .type_chart import TYPE_NAMES, TypeChart, build_defensive_vector


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POKEMON_PATH = PROJECT_ROOT / "data" / "pokemon.json"
DEFAULT_TYPE_CHART_PATH = PROJECT_ROOT / "data" / "type_chart.json"
SINGLE_TYPE_MULTIPLIERS = frozenset({0.0, 0.5, 1.0, 2.0})


def _read_json(path: str | Path) -> Any:
    resolved_path = Path(path)
    try:
        with resolved_path.open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError as error:
        raise FileNotFoundError(f"Data file not found: {resolved_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {resolved_path}: {error}") from error


def load_type_chart(
    path: str | Path = DEFAULT_TYPE_CHART_PATH,
) -> dict[str, dict[str, float]]:
    """Load and validate a complete standard 18x18 type chart."""
    raw_chart = _read_json(path)
    if not isinstance(raw_chart, dict):
        raise ValueError("Type chart must be a JSON object")

    expected_types = set(TYPE_NAMES)
    if set(raw_chart) != expected_types:
        missing = expected_types - set(raw_chart)
        extra = set(raw_chart) - expected_types
        raise ValueError(f"Invalid attacking types; missing={missing}, extra={extra}")

    chart: dict[str, dict[str, float]] = {}
    for attack_type in TYPE_NAMES:
        raw_row = raw_chart[attack_type]
        if not isinstance(raw_row, dict) or set(raw_row) != expected_types:
            raise ValueError(
                f"Row {attack_type} must contain exactly the 18 standard types"
            )
        row: dict[str, float] = {}
        for defense_type in TYPE_NAMES:
            value = raw_row[defense_type]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(
                    f"Multiplier {attack_type} -> {defense_type} must be numeric"
                )
            multiplier = float(value)
            if multiplier not in SINGLE_TYPE_MULTIPLIERS:
                raise ValueError(
                    f"Invalid multiplier {attack_type} -> {defense_type}: {value}"
                )
            row[defense_type] = multiplier
        chart[attack_type] = row
    return chart


def load_pokemon(
    path: str | Path = DEFAULT_POKEMON_PATH,
    chart: TypeChart | None = None,
) -> tuple[Pokemon, ...]:
    """Load Pokemon records and precompute their defensive vectors."""
    raw_records = _read_json(path)
    if not isinstance(raw_records, list):
        raise ValueError("Pokemon data must be a JSON array")
    if not raw_records:
        raise ValueError("Pokemon data cannot be empty")

    effective_chart = chart if chart is not None else load_type_chart()
    pokemon: list[Pokemon] = []
    required_fields = {"id", "name", "api_name", "type1", "type2"}
    for index, record in enumerate(raw_records):
        if not isinstance(record, dict):
            raise ValueError(f"Pokemon record {index} must be an object")
        missing = required_fields - set(record)
        if missing:
            raise ValueError(f"Pokemon record {index} is missing fields: {missing}")
        if isinstance(record["id"], bool) or not isinstance(record["id"], int):
            raise ValueError(f"Pokemon record {index} has an invalid id")
        for field in ("name", "api_name", "type1"):
            if not isinstance(record[field], str):
                raise ValueError(f"Pokemon record {index} has invalid {field}")
        if record["type2"] is not None and not isinstance(record["type2"], str):
            raise ValueError(f"Pokemon record {index} has invalid type2")

        pokemon.append(
            Pokemon(
                id=record["id"],
                name=record["name"],
                api_name=record["api_name"],
                type1=record["type1"],
                type2=record["type2"],
                defensive_vector=build_defensive_vector(
                    effective_chart, record["type1"], record["type2"]
                ),
            )
        )

    ids = [item.id for item in pokemon]
    names = [item.name for item in pokemon]
    api_names = [item.api_name for item in pokemon]
    if len(ids) != len(set(ids)):
        raise ValueError("Pokemon ids must be unique")
    if len(names) != len(set(names)):
        raise ValueError("Pokemon display names must be unique")
    if len(api_names) != len(set(api_names)):
        raise ValueError("Pokemon API names must be unique")
    return tuple(pokemon)


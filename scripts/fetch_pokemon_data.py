"""Create the project's offline Pokemon and type-chart data snapshot.

Only this development utility contacts PokeAPI. The optimizer itself reads the
generated JSON files from ``data/`` and therefore works without internet.
"""

from __future__ import annotations

import argparse
import json
import random
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


API_BASE = "https://pokeapi.co/api/v2"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
STANDARD_TYPES = (
    "normal",
    "fire",
    "water",
    "electric",
    "grass",
    "ice",
    "fighting",
    "poison",
    "ground",
    "flying",
    "psychic",
    "bug",
    "rock",
    "ghost",
    "dragon",
    "dark",
    "steel",
    "fairy",
)
USER_AGENT = (
    "Pokemon-Team-Optimization-PKO/1.0 "
    "(https://github.com/phantzzy/Pokemon-Team-Optimziation---PKO)"
)


def fetch_json(url: str, retries: int = 4) -> dict[str, Any]:
    """Fetch one JSON object, retrying temporary HTTP/network failures."""
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            if attempt == retries - 1:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("unreachable")


def get_all_species() -> list[dict[str, str]]:
    """Return every species reference currently exposed by PokeAPI."""
    payload = fetch_json(f"{API_BASE}/pokemon-species?limit=100000&offset=0")
    return sorted(payload["results"], key=_resource_id)


def _resource_id(resource: dict[str, str]) -> int:
    return int(resource["url"].rstrip("/").rsplit("/", 1)[-1])


def choose_species(
    species: list[dict[str, str]], count: int | None, seed: int
) -> list[dict[str, str]]:
    """Choose a deterministic cross-generation sample, or all species."""
    if count is None or count >= len(species):
        return species
    if count < 6:
        raise ValueError("--count must be at least 6")
    rng = random.Random(seed)
    return sorted(rng.sample(species, count), key=_resource_id)


def fetch_default_pokemon(species_ref: dict[str, str]) -> dict[str, Any]:
    """Fetch one species and reduce its default variety to fields we need."""
    species = fetch_json(species_ref["url"])
    default_varieties = [
        variety["pokemon"]
        for variety in species["varieties"]
        if variety["is_default"]
    ]
    if len(default_varieties) != 1:
        raise ValueError(
            f"Expected one default variety for {species['name']}, "
            f"found {len(default_varieties)}"
        )

    pokemon = fetch_json(default_varieties[0]["url"])
    english_names = [
        item["name"]
        for item in species["names"]
        if item["language"]["name"] == "en"
    ]
    if len(english_names) != 1:
        raise ValueError(f"Missing unique English name for {species['name']}")

    ordered_types = [
        entry["type"]["name"]
        for entry in sorted(pokemon["types"], key=lambda entry: entry["slot"])
    ]
    if not 1 <= len(ordered_types) <= 2:
        raise ValueError(f"Invalid type count for {species['name']}")
    if any(type_name not in STANDARD_TYPES for type_name in ordered_types):
        raise ValueError(f"Non-standard type for {species['name']}: {ordered_types}")

    return {
        "id": species["id"],
        "name": english_names[0],
        "api_name": pokemon["name"],
        "type1": ordered_types[0].title(),
        "type2": ordered_types[1].title() if len(ordered_types) == 2 else None,
    }


def fetch_pokemon_dataset(
    selected_species: list[dict[str, str]], workers: int
) -> list[dict[str, Any]]:
    """Fetch selected species concurrently and return them in National Dex order."""
    records: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(fetch_default_pokemon, species): species
            for species in selected_species
        }
        completed = 0
        for future in as_completed(futures):
            records.append(future.result())
            completed += 1
            if completed % 25 == 0 or completed == len(futures):
                print(f"Fetched Pokemon: {completed}/{len(futures)}")
    return sorted(records, key=lambda record: record["id"])


def fetch_type_chart() -> dict[str, dict[str, float]]:
    """Build an attack-type -> defense-type multiplier matrix."""
    chart: dict[str, dict[str, float]] = {}
    for attack_type in STANDARD_TYPES:
        relations = fetch_json(f"{API_BASE}/type/{attack_type}")["damage_relations"]
        row = {defense_type.title(): 1.0 for defense_type in STANDARD_TYPES}
        for relation_name, multiplier in (
            ("no_damage_to", 0.0),
            ("half_damage_to", 0.5),
            ("double_damage_to", 2.0),
        ):
            for target in relations[relation_name]:
                if target["name"] in STANDARD_TYPES:
                    row[target["name"].title()] = multiplier
        chart[attack_type.title()] = row
    return chart


def validate_snapshot(
    pokemon: list[dict[str, Any]], chart: dict[str, dict[str, float]]
) -> None:
    """Reject incomplete, duplicate, or obviously incorrect snapshots."""
    names = [record["name"] for record in pokemon]
    if len(names) != len(set(names)):
        raise ValueError("Pokemon names must be unique")
    expected_types = {name.title() for name in STANDARD_TYPES}
    if set(chart) != expected_types:
        raise ValueError("Type chart does not contain exactly the 18 standard types")
    if any(set(row) != expected_types for row in chart.values()):
        raise ValueError("Type chart is not a complete 18x18 matrix")

    known_matchups = {
        ("Electric", "Ground"): 0.0,
        ("Fire", "Grass"): 2.0,
        ("Fire", "Water"): 0.5,
        ("Normal", "Ghost"): 0.0,
        ("Fighting", "Normal"): 2.0,
        ("Ice", "Dragon"): 2.0,
    }
    for (attack, defense), expected in known_matchups.items():
        actual = chart[attack][defense]
        if actual != expected:
            raise ValueError(
                f"Unexpected matchup {attack} -> {defense}: {actual} != {expected}"
            )


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="number of species to sample (default: 100); use 0 for all species",
    )
    parser.add_argument(
        "--seed", type=int, default=2026, help="sampling seed (default: 2026)"
    )
    parser.add_argument(
        "--workers", type=int, default=8, help="concurrent API requests (default: 8)"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.count < 0:
        raise SystemExit("--count cannot be negative")
    if args.workers < 1:
        raise SystemExit("--workers must be positive")

    all_species = get_all_species()
    selected = choose_species(all_species, args.count or None, args.seed)
    print(
        f"PokeAPI exposes {len(all_species)} species; fetching {len(selected)} "
        f"default forms (seed={args.seed})."
    )
    pokemon = fetch_pokemon_dataset(selected, args.workers)
    chart = fetch_type_chart()
    validate_snapshot(pokemon, chart)
    write_json(DATA_DIR / "pokemon.json", pokemon)
    write_json(DATA_DIR / "type_chart.json", chart)
    print(f"Wrote {len(pokemon)} Pokemon to {DATA_DIR / 'pokemon.json'}")
    print(f"Wrote 18x18 type chart to {DATA_DIR / 'type_chart.json'}")


if __name__ == "__main__":
    main()


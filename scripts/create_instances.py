"""Create the five fixed, nested problem instances from local Pokemon data."""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pokemon_opt.data_loader import load_pokemon  # noqa: E402


INSTANCES_DIR = PROJECT_ROOT / "instances"
INSTANCE_SIZES = {
    "small_12": 12,
    "medium_20": 20,
    "medium_30": 30,
    "large_50": 50,
    "xlarge_100": 100,
}
SEED = 2026


def main() -> None:
    pokemon = list(load_pokemon())
    largest_size = max(INSTANCE_SIZES.values())
    if len(pokemon) < largest_size:
        raise ValueError(
            f"Dataset needs at least {largest_size} Pokemon; found {len(pokemon)}"
        )

    rng = random.Random(SEED)
    rng.shuffle(pokemon)
    INSTANCES_DIR.mkdir(parents=True, exist_ok=True)

    for name, size in INSTANCE_SIZES.items():
        payload = {
            "name": name,
            "pokemon": [item.name for item in pokemon[:size]],
        }
        output_path = INSTANCES_DIR / f"{name}.json"
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {name}: {size} Pokemon -> {output_path}")


if __name__ == "__main__":
    main()

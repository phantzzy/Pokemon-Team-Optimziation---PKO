# Data

The files in this directory are a local snapshot derived from
[PokéAPI](https://pokeapi.co/). PokéAPI is a community-maintained project and
is not an official Nintendo or The Pokémon Company API.

`pokemon.json` contains a fixed, cross-generation sample of 100 unique Pokémon
species selected with seed `2026`. For each species, only its default variety
is retained. Alternate forms, Mega Evolutions, and Gigantamax forms are not
included. Each record stores the National Pokédex species ID, English display
name, PokéAPI resource name, and one or two defensive types.

`type_chart.json` is a complete 18x18 matrix. Top-level keys are attacking
types, nested keys are defending types, and values are effectiveness
multipliers. It is generated from the current `damage_relations` returned by
PokéAPI's Type endpoint.

The snapshot was generated on 2026-10-07 with:

```powershell
python scripts/fetch_pokemon_data.py --count 100 --seed 2026
```

The generated files are committed so the optimizer and tests never require an
internet connection. Re-running the command may change the snapshot if PokéAPI
changes its underlying data.

Pokémon and Pokémon character names are trademarks of Nintendo. PokéAPI's
software and data snapshot are distributed under the BSD 3-Clause license;
see `POKEAPI_LICENSE.txt` in this directory.


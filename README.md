# Roblox-Asset-Varietor

All of those may require you have your `.ROBLOSECURITY` cookie either as a command-line argument or in a system environmental variable called `ROBLOSECURITY`.

- ## [`anims.py`](./anims.py)

Generates a file [`anims.json`](./anims.json) with _all of_ Rōblox's animation bundle hotlinks and their associated asset IDs. The file [`anims-old.json`](./anims-old.json) was generated in late 2022; many of the animation IDs are absent in `anims.json`.

- ## [`places.py`](./places.py)

Allows you to search for places or list all the games in Rōblox's discover page (about a few thousand in all) and updated [`places.json`](./places.json) with it.

- ## [`catalogue.py`](./catalogue.py)

Uses Rōblox's toolbox search API query string and asset type (such as model, decal, etc.) and generates a file [`catalogue.json`](./catalogue.json) with the results.

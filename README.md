# Minecraft Region Item Finder

A zero-dependency, ultra-fast Python CLI tool to locate misplaced chests, shulker boxes, armor, custom-named items, and containers across modern and legacy Minecraft worlds (`.mca` Anvil format).

> 🤖 **Built with [Google Gemini](https://gemini.google.com/)**

---

## Features

- **Zero Dependencies:** Pure Python 3.8+ using standard libraries (`zlib`, `struct`, `argparse`). No extra packages to install.
- **Custom Name Support:** Easily search for anvil-renamed items and containers (e.g., a shulker box named `"Fireworks"`).
- **Exact Coordinates:** Reads container NBT data to extract precise block coordinates (`X`, `Y`, `Z`), with fallback chunk-level coordinates.
- **Modern & Legacy Support:** Fully compatible with Minecraft 1.18+ / 1.20+ height limits, custom dimensions, and legacy Anvil region structures.
- **Multi-Launcher Compatible:** Works with vanilla saves, Prism Launcher, Modrinth App, and CurseForge directories.

---

## Installation

Clone the repository:

```bash
git clone [https://github.com/](https://github.com/)<your-username>/minecraft-item-finder.git
cd minecraft-item-finder

---

## Usage
python mc_item_finder.py "<path_to_region_folder>" -q <target_query_1> [target_query_2 ...]

---


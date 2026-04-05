# Vassar Arboretum Tree Map

A fast, mobile-friendly interactive map of the [Vassar College Arboretum](https://www.vassar.edu/arboretum) — built because the official map is too slow to use while walking campus.

**[→ Open the map](https://htmlpreview.github.io/?https://github.com/davdgreen/vassar-tree-map/blob/main/vassar-tree-map.html)**

> Or enable GitHub Pages (repo Settings → Pages → Source: main branch) for a cleaner URL at `https://davdgreen.github.io/vassar-tree-map`

## Features

- **Instant search** — type any tree name and results appear in ~150ms
- **2,479 trees, 168 species** — full campus inventory
- **Rich popups** — Tree ID, common name, scientific name, age class, condition class
- **My Location** — shows your position on the map while walking campus
- **Single file** — no server, no install, works in any browser

## Usage

Open `vassar-tree-map.html` in a browser. Requires an internet connection for map tiles (OpenStreetMap) — all tree data is embedded locally.

Search examples:
- `dawn redwood` → highlights all 5 on campus, flies to fit them
- `maple` → shows all maple varieties (Red, Sugar, Japanese, etc.)
- `oak` → every oak on campus

## Files

| File | Description |
|------|-------------|
| `vassar-tree-map.html` | The map — open this in a browser |
| `build_vassar_map.py` | Regenerates the HTML from source data |
| `vassar_arboretum.csv` | 2,479 trees with coordinates and species |
| `vassar_enriched.json` | Scientific names, age class, condition class (scraped from ArborScope) |
| `vassar_arboretum_species.json` | 168 unique species with campus counts |

## Rebuilding

To regenerate the map after editing data:

```bash
python3 build_vassar_map.py
```

## Data Source

Tree inventory from the [Vassar College ArborScope](https://arborscope.com/mapDisplay.cfm?id=08CCC6C7) system, maintained by Bartlett Tree Experts.

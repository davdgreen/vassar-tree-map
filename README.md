# Vassar Arboretum Tree Map

A fast, mobile-friendly interactive map of the [Vassar College Arboretum](https://www.vassar.edu/arboretum) — built because the official map is too slow to use while walking campus.

**[→ Open the map](https://davdgreen.github.io/vassar-tree-map/)**

## Features

- **Instant search** — type any tree name and results appear in ~150ms
- **2,479 trees, 168 species** — full campus inventory
- **Rich popups** — Tree ID, common name, scientific name, age class, condition class; rare species flagged with "1 of only N on campus"
- **Follow mode** — tap 📍 to track your GPS as you walk; drag the map to pause, tap again to re-engage
- **Take me there** — tap any tree, then "🚶 Take me there" for a walking route directly to that tree
- **In Season** — highlights what's blooming, fruiting, or turning color on any date; tap a category to select the whole group; walk route through seasonal highlights
- **Mobile-first** — works in Chrome on Android/iOS over HTTPS

## Usage

Open the map at `https://davdgreen.github.io/vassar-tree-map/`. Requires an internet connection for map tiles and walking routes — all tree data is embedded in the page.

Location features require HTTPS (already provided by GitHub Pages). Opening the HTML file directly from device storage will block geolocation on mobile Chrome.

Search examples:
- `dawn redwood` → highlights all 5 on campus, flies to fit them
- `maple` → shows all maple varieties (Red, Sugar, Japanese, etc.)
- `oak` → every oak on campus

## Files

| File | Description |
|------|-------------|
| `index.html` | The map — served by GitHub Pages at the URL above |
| `vassar-tree-map.html` | Duplicate of `index.html` (kept for local testing) |
| `favicon.svg` | Tree icon shown in browser tabs and home screen bookmarks |
| `build_vassar_map.py` | Regenerates the HTML from source data |
| `build_seasonal_data.py` | Generates `vassar_seasonal.json` from species data |
| `vassar_arboretum.csv` | 2,479 trees with coordinates and species |
| `vassar_enriched.json` | Scientific names, age class, condition class (scraped from ArborScope) |
| `vassar_arboretum_species.json` | 168 unique species with campus counts |
| `vassar_seasonal.json` | Seasonal event data — bloom/color/fruit windows per species |

## Rebuilding

To regenerate the map after editing data:

```bash
python3 build_vassar_map.py
```

## Data Source

Tree inventory from the [Vassar College ArborScope](https://arborscope.com/mapDisplay.cfm?id=08CCC6C7) system, maintained by Bartlett Tree Experts.

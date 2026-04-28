#!/usr/bin/env python3
"""
Scrape the Vassar arboretum inventory from ArborScope and rebuild source data files.

Endpoints (discovered from map.js):
  generateTrees.cfm  — returns JSON array of all tree positions
  getInfoWindow.cfm  — returns HTML fragment with enriched data per tree

Usage:
  python3 scrape_arborscope.py           # full scrape, overwrite source files
  python3 scrape_arborscope.py --verify  # compare against existing files, no writes
"""

import argparse
import csv
import json
import re
import time

import requests
from bs4 import BeautifulSoup

INVENTORY_ID = '08CCC6C7'
BASE_URL = 'https://arborscope.com'
MAP_URL = f'{BASE_URL}/mapDisplay.cfm?id={INVENTORY_ID}'
TREES_URL = f'{BASE_URL}/includes/generateTrees.cfm'
INFO_URL = f'{BASE_URL}/includes/getInfoWindow.cfm'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'Referer': MAP_URL,
}

CSV_PATH = 'vassar_arboretum.csv'
ENRICHED_PATH = 'vassar_enriched.json'


# ---------------------------------------------------------------------------
# Session setup — visit main page to get cookies, hidden form params, species list
# ---------------------------------------------------------------------------

def make_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    print('Fetching main page for session cookies...')
    r = s.get(MAP_URL, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, 'html.parser')
    form = soup.find('form', id='FilterForm')

    hidden_params = {}
    species_names = []
    if form:
        for inp in form.find_all('input', type='hidden'):
            name = inp.get('name')
            val = inp.get('value', '')
            if name:
                hidden_params[name] = val

        # Extract canonical common names from the dropdown (these are in "Maple-Red" format)
        name_select = form.find('select', {'name': 'commonName'})
        if name_select:
            for opt in name_select.find_all('option'):
                val = (opt.get('value') or opt.get_text()).strip()
                if val and val.lower() not in ('', 'all'):
                    species_names.append(val)

    print(f'  Session established. {len(species_names)} species in dropdown.')
    return s, hidden_params, species_names


# ---------------------------------------------------------------------------
# Step 1a: fetch all tree positions from generateTrees.cfm
# ---------------------------------------------------------------------------

def fetch_trees(session, hidden_params):
    print('Fetching tree list from generateTrees.cfm...')
    r = session.get(TREES_URL, params=dict(hidden_params), timeout=60)
    r.raise_for_status()

    data = r.json()
    # Structure: {"trees": [[treeid, featureid, lat, lng, color_hex, grid], ...]}
    raw = data.get('trees', [])
    trees = []
    for entry in raw:
        treeid, featureid, lat, lng, color, grid = entry[0], entry[1], entry[2], entry[3], entry[4], entry[5]
        # treeid = internal sequential ID; featureid = Bartlett's ID (bartlett_id in our CSV)
        # color is already a hex string like '009b04' or 'ffff00'
        trees.append({
            'internal_id': str(treeid),
            'bartlett_id': str(featureid),
            'lat':         float(lat),
            'lng':         float(lng),
            'color_code':  str(color),
        })
    print(f'  Got {len(trees)} trees.')
    return trees


# ---------------------------------------------------------------------------
# Step 1b: build bartlett_id -> common_name by filtering once per species
# ---------------------------------------------------------------------------

def fetch_name_map(session, hidden_params, species_names, delay=0.05):
    """
    Call generateTrees.cfm once per species with a commonName filter to get
    the authoritative "Maple-Red" format name for each bartlett_id.
    """
    print(f'Building name map ({len(species_names)} species)...')
    name_map = {}
    for i, name in enumerate(species_names):
        params = dict(hidden_params)
        params['commonName'] = name
        r = session.get(TREES_URL, params=params, timeout=30)
        r.raise_for_status()
        for entry in r.json().get('trees', []):
            featureid = str(entry[1])
            name_map[featureid] = name
        if (i + 1) % 30 == 0 or i == 0:
            print(f'  {i+1}/{len(species_names)} species...')
        time.sleep(delay)
    print(f'  Name map built: {len(name_map)} trees across {len(species_names)} species.')
    return name_map


# ---------------------------------------------------------------------------
# Step 2: fetch enriched info for each tree from getInfoWindow.cfm
# ---------------------------------------------------------------------------

def parse_info_window(html):
    """
    Extract sci, age, cond from getInfoWindow HTML fragment.

    Actual structure (from ArborScope):
      <h3><a ...><span>Tree ID: NNN</span><br/><strong>Red Maple</strong></a></h3>
      <p><i>Acer rubrum</i></p>
      <p>Age Class: <em>Semi-mature</em></p>
      <p>Condition Class: <em>Good</em></p>
    """
    soup = BeautifulSoup(html, 'html.parser')
    result = {}

    details = soup.find(class_='info-window-details')
    if details:
        i_tag = details.find('i')
        if i_tag:
            result['sci'] = i_tag.get_text(strip=True)

        for p in details.find_all('p'):
            em = p.find('em')
            if not em:
                continue
            text = p.get_text(separator=' ', strip=True)
            val = em.get_text(strip=True)
            if re.search(r'Age Class', text, re.I):
                result['age'] = val
            elif re.search(r'Condition Class', text, re.I):
                result['cond'] = val

    return result


def fetch_enriched(session, trees, delay=0.1):
    enriched = {}
    total = len(trees)
    for i, t in enumerate(trees):
        bid = t['bartlett_id']
        params = {
            'id':        INVENTORY_ID,
            'treeid':    bid,
            'featureID': bid,
            'icon':      t['color_code'],
        }
        r = session.get(INFO_URL, params=params, timeout=30)
        r.raise_for_status()
        info = parse_info_window(r.text)
        enriched[bid] = {
            'sci':  info.get('sci', ''),
            'age':  info.get('age', ''),
            'cond': info.get('cond', ''),
        }
        if (i + 1) % 100 == 0 or i == 0:
            print(f'  Enriched {i+1}/{total}...')
        time.sleep(delay)

    print(f'  Enriched all {total} trees.')
    return enriched


# ---------------------------------------------------------------------------
# Write output files
# ---------------------------------------------------------------------------

def write_csv(trees, name_map, enriched, path):
    rows = []
    for t in trees:
        bid = t['bartlett_id']
        info = enriched.get(bid, {})
        rows.append({
            'internal_id': t['internal_id'],
            'bartlett_id': bid,
            'common_name': name_map.get(bid, ''),
            'genus':       info.get('sci', '').split()[0] if info.get('sci') else '',
            'latitude':    f"{t['lat']:.9f}",
            'longitude':   f"{t['lng']:.9f}",
            'color_code':  t['color_code'],
        })
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'internal_id', 'bartlett_id', 'common_name',
            'genus', 'latitude', 'longitude', 'color_code',
        ])
        writer.writeheader()
        writer.writerows(rows)
    print(f'Wrote {len(rows)} rows to {path}')


def write_enriched(enriched, path):
    out = {bid: {'sci': v['sci'], 'age': v['age'], 'cond': v['cond']}
           for bid, v in enriched.items()}
    with open(path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f'Wrote {len(out)} entries to {path}')


# ---------------------------------------------------------------------------
# Verify mode: compare scraped data against existing files
# ---------------------------------------------------------------------------

def verify(trees, name_map, enriched):
    print('\n=== VERIFICATION ===')

    existing_csv = {}
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            existing_csv[row['bartlett_id']] = row

    with open(ENRICHED_PATH) as f:
        existing_enriched = json.load(f)

    scraped_ids = {t['bartlett_id'] for t in trees}
    existing_ids = set(existing_csv.keys())

    added   = scraped_ids - existing_ids
    removed = existing_ids - scraped_ids
    if added:
        print(f'NEW trees ({len(added)}): {sorted(added)[:10]}{"..." if len(added) > 10 else ""}')
        for bid in sorted(added):
            print(f'  [{bid}] {name_map.get(bid, "?")}')
    if removed:
        print(f'REMOVED trees ({len(removed)}): {sorted(removed)[:10]}{"..." if len(removed) > 10 else ""}')
    if not added and not removed:
        print(f'Tree count matches: {len(scraped_ids)} trees')

    # Check enriched fields
    changed = []
    for bid in scraped_ids & existing_ids:
        old = existing_enriched.get(bid, {})
        new = enriched.get(bid, {})
        diffs = {k: (old.get(k), new.get(k))
                 for k in ('sci', 'age', 'cond')
                 if old.get(k) != new.get(k)}
        if diffs:
            changed.append((bid, diffs))

    if changed:
        print(f'\nChanged enriched data ({len(changed)} trees):')
        for bid, diffs in changed[:20]:
            name = existing_csv.get(bid, {}).get('common_name', bid)
            for field, (old, new) in diffs.items():
                print(f'  [{bid}] {name}: {field}: {old!r} -> {new!r}')
        if len(changed) > 20:
            print(f'  ... and {len(changed) - 20} more')
    else:
        print('No enriched data changes.')

    # Spot-check coordinates
    coord_diffs = []
    for t in trees:
        bid = t['bartlett_id']
        if bid not in existing_csv:
            continue
        old_lat = float(existing_csv[bid]['latitude'])
        old_lng = float(existing_csv[bid]['longitude'])
        if abs(t['lat'] - old_lat) > 1e-6 or abs(t['lng'] - old_lng) > 1e-6:
            coord_diffs.append((bid, old_lat, old_lng, t['lat'], t['lng']))
    if coord_diffs:
        print(f'\nCoordinate changes ({len(coord_diffs)} trees):')
        for bid, olat, olng, nlat, nlng in coord_diffs[:10]:
            print(f'  [{bid}]: ({olat},{olng}) -> ({nlat},{nlng})')
    else:
        print('No coordinate changes.')

    print(f'\nVerification complete. {len(added)} added, {len(removed)} removed, {len(changed)} enriched changes.')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--verify', action='store_true',
                        help='Compare against existing files without writing')
    parser.add_argument('--delay', type=float, default=0.1,
                        help='Seconds between getInfoWindow requests (default 0.1)')
    parser.add_argument('--limit', type=int, default=None,
                        help='Only process first N trees (for testing)')
    args = parser.parse_args()

    session, hidden_params, species_names = make_session()
    trees = fetch_trees(session, hidden_params)
    name_map = fetch_name_map(session, hidden_params, species_names)

    if args.limit:
        trees = trees[:args.limit]
        print(f'(Limited to first {args.limit} trees)')

    enriched = fetch_enriched(session, trees, delay=args.delay)

    if args.verify:
        verify(trees, name_map, enriched)
    else:
        write_csv(trees, name_map, enriched, CSV_PATH)
        write_enriched(enriched, ENRICHED_PATH)
        print('\nDone. Run `python3 build_vassar_map.py` to rebuild index.html.')


if __name__ == '__main__':
    main()

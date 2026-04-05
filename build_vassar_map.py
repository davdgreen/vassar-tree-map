import csv, json
from collections import Counter

# Read enriched data
enriched = json.load(open('vassar_enriched.json'))

# Read seasonal data
seasonal = json.load(open('vassar_seasonal.json'))

# Read tree data
trees = []
with open('vassar_arboretum.csv') as f:
    for row in csv.DictReader(f):
        bid = row['bartlett_id']
        extra = enriched.get(bid, {})
        genus = row['genus'].strip()
        name = row['common_name']
        sp_seasonal = seasonal.get(name, {})
        trees.append({
            'id': int(row['internal_id']),
            'bid': bid,
            'name': name,
            'genus': genus,
            'sci': extra.get('sci', ''),
            'age': extra.get('age', ''),
            'cond': extra.get('cond', ''),
            'lat': float(row['latitude']),
            'lng': float(row['longitude']),
            'color': '#' + row['color_code'],
        })

# Build filter option lists (sorted, with counts)
name_counts  = Counter(t['name']  for t in trees)
genus_counts = Counter(t['genus'] for t in trees)
age_counts   = Counter(t['age']   for t in trees if t['age'])
cond_counts  = Counter(t['cond']  for t in trees if t['cond'])

age_order  = ['New planting', 'Young', 'Semi-mature', 'Mature', 'Over-mature']
cond_order = ['Good', 'Fair', 'Poor', 'Dead', 'ASAP']

name_opts  = sorted(name_counts.items(),  key=lambda x: x[0])
genus_opts = sorted(genus_counts.items(), key=lambda x: x[0])
age_opts   = [(a, age_counts[a])  for a in age_order  if a in age_counts]
cond_opts  = [(c, cond_counts[c]) for c in cond_order if c in cond_counts]

def opts_html(pairs, all_label):
    lines = [f'<option value="">— {all_label} —</option>']
    for val, count in pairs:
        lines.append(f'<option value="{val}">{val} ({count})</option>')
    return '\n'.join(lines)

name_opts_html  = opts_html(name_opts,  'All species')
genus_opts_html = opts_html(genus_opts, 'All genera')
age_opts_html   = opts_html(age_opts,   'Any age')
cond_opts_html  = opts_html(cond_opts,  'Any condition')

trees_json = json.dumps(trees, separators=(',', ':'))

# Seasonal lookup keyed by common_name: name -> list of events
# Only include fields needed by JS (drop 'sci' since trees already have it)
seasonal_js = {
    name: [
        {k: v for k, v in ev.items()}
        for ev in data['events']
    ]
    for name, data in seasonal.items()
}
seasonal_json = json.dumps(seasonal_js, separators=(',', ':'))

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>Vassar Arboretum</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet-routing-machine@3.2.12/dist/leaflet-routing-machine.css"/>
<script src="https://unpkg.com/leaflet-routing-machine@3.2.12/dist/leaflet-routing-machine.min.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ height: 100%; overflow: hidden; font-family: -apple-system, sans-serif; }}

#map {{ position: absolute; inset: 0; }}

/* ── Top UI panel ── */
#ui {{
  position: absolute;
  top: 12px; left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  width: min(460px, calc(100vw - 24px));
}}

#search-wrap {{
  display: flex;
  flex-direction: column;
  background: rgba(255,255,255,0.97);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.25);
  padding: 10px 14px;
  gap: 8px;
}}

#search-row {{
  display: flex;
  align-items: center;
  gap: 8px;
}}

#search {{
  flex: 1;
  border: none;
  outline: none;
  font-size: 17px;
  background: transparent;
  color: #111;
  min-width: 0;
}}
#search::placeholder {{ color: #aaa; }}

#clear-btn {{
  display: none;
  background: none;
  border: none;
  font-size: 20px;
  color: #888;
  cursor: pointer;
  line-height: 1;
  padding: 0 2px;
  flex-shrink: 0;
}}

/* Button row below search */
#btn-row {{
  display: flex;
  gap: 8px;
}}

/* Filter toggle button */
#filter-toggle {{
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  background: none;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 14px;
  color: #555;
  cursor: pointer;
  white-space: nowrap;
  transition: border-color 0.15s, color 0.15s;
}}
#filter-toggle.active {{
  border-color: #2e7d32;
  color: #2e7d32;
  background: rgba(46,125,50,0.07);
}}
#filter-badge {{
  display: none;
  background: #2e7d32;
  color: white;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
  padding: 1px 6px;
  margin-left: 2px;
}}

/* Season toggle button */
#season-toggle {{
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  background: none;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 14px;
  color: #555;
  cursor: pointer;
  white-space: nowrap;
  transition: border-color 0.15s, color 0.15s;
}}
#season-toggle.active {{
  border-color: #e65100;
  color: #e65100;
  background: rgba(230,81,0,0.07);
}}

/* Filter panel */
#filter-panel {{
  display: none;
  margin-top: 8px;
  background: rgba(255,255,255,0.97);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.2);
  padding: 14px;
  gap: 10px;
  flex-direction: column;
}}
#filter-panel.open {{ display: flex; }}

.filter-row {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}}

.filter-group label {{
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}}

.filter-group select {{
  width: 100%;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  padding: 7px 10px;
  font-size: 13px;
  color: #222;
  background: white;
  outline: none;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='%23999' d='M6 8L0 0h12z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  padding-right: 28px;
}}
.filter-group select:focus {{ border-color: #2e7d32; }}
.filter-group select.set {{ border-color: #2e7d32; background-color: rgba(46,125,50,0.05); }}

#filter-clear {{
  align-self: flex-end;
  background: none;
  border: none;
  font-size: 12px;
  color: #e53935;
  cursor: pointer;
  padding: 2px 0;
  display: none;
}}

/* Season panel */
#season-panel {{
  display: none;
  margin-top: 8px;
  background: rgba(255,255,255,0.97);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.2);
  padding: 14px;
  flex-direction: column;
  gap: 12px;
  max-height: calc(100vh - 140px);
  overflow-y: auto;
}}
#season-panel.open {{ display: flex; }}

.panel-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
}}
.panel-title {{
  font-size: 13px;
  font-weight: 700;
  color: #555;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}
.panel-header-btns {{
  display: flex;
  gap: 4px;
}}
.panel-hdr-btn {{
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #aaa;
  padding: 2px 6px;
  border-radius: 6px;
  line-height: 1;
  transition: background 0.1s, color 0.1s;
}}
.panel-hdr-btn:hover {{ background: #f0f0f0; color: #333; }}
#exit-season-btn {{ color: #e53935; }}
#exit-season-btn:hover {{ background: rgba(229,57,53,0.1); color: #e53935; }}

.season-date-row {{
  display: flex;
  align-items: center;
  gap: 10px;
}}
.season-date-row label {{
  font-size: 12px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  white-space: nowrap;
}}
#season-date {{
  flex: 1;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 14px;
  color: #222;
  outline: none;
}}
#season-date:focus {{ border-color: #e65100; }}

.season-actions {{
  display: flex;
  gap: 8px;
}}

.season-btn {{
  flex: 1;
  padding: 8px 12px;
  border-radius: 8px;
  border: none;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}}
#show-all-season {{
  background: #e65100;
  color: white;
}}
#show-all-season:hover {{ background: #bf360c; }}
#walk-route-btn {{
  background: #1565c0;
  color: white;
}}
#walk-route-btn:hover {{ background: #0d47a1; }}
#clear-route-btn {{
  display: none;
  background: #666;
  color: white;
}}
#clear-route-btn:hover {{ background: #444; }}

.season-group {{
  display: flex;
  flex-direction: column;
  gap: 4px;
}}
.season-group-header {{
  font-size: 11px;
  font-weight: 700;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 4px 0 2px;
  border-bottom: 1px solid #eee;
}}
.season-species-row {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 7px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.1s;
}}
.season-species-row:hover {{ background: #f5f5f5; }}
.season-species-row.active {{
  background: rgba(230,81,0,0.1);
  outline: 1.5px solid rgba(230,81,0,0.3);
}}
.season-species-name {{
  font-size: 14px;
  font-weight: 500;
  color: #111;
}}
.season-species-sub {{
  font-size: 11px;
  color: #888;
  margin-top: 1px;
}}
.season-species-count {{
  font-size: 12px;
  color: #888;
  white-space: nowrap;
  padding-left: 8px;
}}
.season-empty {{
  font-size: 14px;
  color: #888;
  text-align: center;
  padding: 16px 0;
}}

.route-info {{
  font-size: 13px;
  color: #555;
  background: rgba(21,101,192,0.08);
  border-radius: 8px;
  padding: 8px 12px;
  display: none;
}}

/* Status bar */
#status {{
  margin-top: 6px;
  padding: 5px 12px;
  background: rgba(0,0,0,0.72);
  color: #fff;
  border-radius: 8px;
  font-size: 13px;
  text-align: center;
  display: none;
}}

/* Popup */
.pp-id   {{ font-size: 12px; color: #666; margin-bottom: 3px; }}
.pp-name {{ font-size: 15px; font-weight: 600; color: #111; margin-bottom: 2px; }}
.pp-sci  {{ font-size: 13px; font-style: italic; color: #444; margin-bottom: 6px; }}
.pp-row  {{ font-size: 12px; color: #333; margin-top: 3px; }}
.pp-lbl  {{ color: #666; }}
.pp-season {{ font-size: 12px; color: #e65100; margin-top: 6px; padding-top: 6px; border-top: 1px solid #eee; }}

/* Location button */
#locate-btn {{
  position: absolute;
  bottom: 32px; right: 12px;
  z-index: 1000;
  width: 46px; height: 46px;
  border-radius: 50%;
  background: white;
  border: none;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  font-size: 22px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}}

/* Pulsing season marker */
@keyframes pulse {{
  0%   {{ box-shadow: 0 0 0 0 rgba(230,81,0,0.5); }}
  70%  {{ box-shadow: 0 0 0 8px rgba(230,81,0,0); }}
  100% {{ box-shadow: 0 0 0 0 rgba(230,81,0,0); }}
}}
</style>
</head>
<body>

<div id="map"></div>

<div id="ui">

  <!-- Search box -->
  <div id="search-wrap">
    <div id="search-row">
      <span style="font-size:18px;color:#888;flex-shrink:0">🔍</span>
      <input id="search" type="search" placeholder="Search trees…" autocomplete="off" autocorrect="off" spellcheck="false">
      <button id="clear-btn" onclick="clearAll()">×</button>
    </div>
    <div id="btn-row">
      <button id="filter-toggle" onclick="toggleFilters()">
        ⚙ Browse <span id="filter-badge"></span>
      </button>
      <button id="season-toggle" onclick="toggleSeason()">🌸 In Season</button>
    </div>
  </div>

  <!-- Filter panel -->
  <div id="filter-panel">

    <div class="filter-row">
      <div class="filter-group">
        <label>Common Name</label>
        <select id="f-name" onchange="applyFilters()">
          {name_opts_html}
        </select>
      </div>
      <div class="filter-group">
        <label>Genus</label>
        <select id="f-genus" onchange="applyFilters()">
          {genus_opts_html}
        </select>
      </div>
    </div>

    <div class="filter-row">
      <div class="filter-group">
        <label>Age Class</label>
        <select id="f-age" onchange="applyFilters()">
          {age_opts_html}
        </select>
      </div>
      <div class="filter-group">
        <label>Condition</label>
        <select id="f-cond" onchange="applyFilters()">
          {cond_opts_html}
        </select>
      </div>
    </div>

    <button id="filter-clear" onclick="clearFilters()">✕ Clear filters</button>
  </div>

  <!-- Season panel -->
  <div id="season-panel">
    <div class="panel-header">
      <span class="panel-title">🌸 In Season</span>
      <div class="panel-header-btns">
        <button class="panel-hdr-btn" onclick="closePanelOnly()" title="Minimize panel">⌄</button>
        <button class="panel-hdr-btn" id="exit-season-btn" onclick="exitSeason()" title="Exit season mode">✕</button>
      </div>
    </div>
    <div class="season-date-row">
      <label>Date</label>
      <input type="date" id="season-date" onchange="renderSeasonPanel()">
    </div>
    <div class="season-actions">
      <button class="season-btn" id="show-all-season" onclick="showAllInSeason()">Show All on Map</button>
      <button class="season-btn" id="walk-route-btn" onclick="buildWalkRoute()">🚶 Walk Route</button>
      <button class="season-btn" id="clear-route-btn" onclick="clearRoute()">✕ Route</button>
    </div>
    <div class="route-info" id="route-info"></div>
    <div id="season-list"></div>
  </div>

  <div id="status"></div>
</div>

<button id="locate-btn" onclick="locateMe()" title="My location">📍</button>

<script>
const TREES = {trees_json};
const SEASONAL = {seasonal_json};

// ── Event type styling ──
const TYPE_COLOR = {{
  bloom:      '#e91e8c',
  fall_color: '#e65100',
  bark:       '#795548',
  fruit:      '#2e7d32',
  foliage:    '#388e3c',
  fragrance:  '#7b1fa2',
}};

// Map
const map = L.map('map', {{ center: [41.6873, -73.8966], zoom: 16, zoomControl: true }});
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
  subdomains: 'abcd', maxZoom: 20
}}).addTo(map);

const layer = L.layerGroup().addTo(map);

// Build allMarkers
const allMarkers = TREES.map(t => {{
  const m = L.circleMarker([t.lat, t.lng], {{
    radius: 5, color: t.color, fillColor: t.color,
    fillOpacity: 0.75, weight: 1.2, opacity: 0.9
  }});

  const ageRow  = t.age  ? `<div class="pp-row"><span class="pp-lbl">Age Class:</span> ${{t.age}}</div>`  : '';
  const condRow = t.cond ? `<div class="pp-row"><span class="pp-lbl">Condition Class:</span> ${{t.cond}}</div>` : '';

  // Active events for today (shown in popup)
  const todayMD = todayMMDD();
  const activeEvs = (SEASONAL[t.name] || []).filter(ev => dateInRange(todayMD, ev.start, ev.end));
  const seasonRow = activeEvs.length
    ? `<div class="pp-season">${{activeEvs.map(e => `${{e.icon}} ${{e.name}}`).join('<br>')}}</div>`
    : '';

  m.bindPopup(
    `<div class="pp-id">Tree ID: ${{t.id}}</div>` +
    `<div class="pp-name">${{t.name}}</div>` +
    `<div class="pp-sci">${{t.sci || t.genus}}</div>` +
    ageRow + condRow + seasonRow,
    {{ maxWidth: 260 }}
  );
  m._treeData = t;
  return m;
}});

// ── Date helpers ──
function todayMMDD() {{
  const d = new Date();
  const mm = String(d.getMonth()+1).padStart(2,'0');
  const dd = String(d.getDate()).padStart(2,'0');
  return `${{mm}}-${{dd}}`;
}}

function dateInRange(mmdd, start, end) {{
  // All strings in MM-DD format. Handle year-wrap (e.g., "11-15" to "02-28").
  if (start <= end) {{
    return mmdd >= start && mmdd <= end;
  }} else {{
    // wraps new year
    return mmdd >= start || mmdd <= end;
  }}
}}

function getExcitingTrees(mmdd) {{
  // Returns array of {{tree, marker, events[]}} for trees with active events on mmdd
  const result = [];
  allMarkers.forEach(m => {{
    const t = m._treeData;
    const active = (SEASONAL[t.name] || []).filter(ev => dateInRange(mmdd, ev.start, ev.end));
    if (active.length) result.push({{ tree: t, marker: m, events: active }});
  }});
  return result;
}}

// ── Filter panel toggle ──
function toggleFilters() {{
  const panel = document.getElementById('filter-panel');
  const btn   = document.getElementById('filter-toggle');
  // Close season panel if open
  if (seasonOpen) toggleSeason();
  panel.classList.toggle('open');
  btn.classList.toggle('active');
}}

// ── Season panel toggle ──
// seasonOpen  = whether the panel is visible
// seasonModeActive = whether trees are currently highlighted in season mode

let seasonModeActive = false;

function toggleSeason() {{
  if (!seasonModeActive) {{
    // Activate season mode and open panel
    seasonModeActive = true;
    seasonOpen = true;
    document.getElementById('filter-panel').classList.remove('open');
    document.getElementById('filter-toggle').classList.remove('active');
    document.getElementById('season-panel').classList.add('open');
    document.getElementById('season-toggle').classList.add('active');
    const inp = document.getElementById('season-date');
    if (!inp.value) inp.value = new Date().toISOString().slice(0,10);
    renderSeasonPanel();
  }} else if (seasonOpen) {{
    // Panel is open — just collapse it, keep highlights
    closePanelOnly();
  }} else {{
    // Panel is closed but season is active — reopen it
    seasonOpen = true;
    document.getElementById('season-panel').classList.add('open');
  }}
}}

function closePanelOnly() {{
  seasonOpen = false;
  document.getElementById('season-panel').classList.remove('open');
  // season-toggle stays orange because season mode is still active
}}

function exitSeason() {{
  seasonModeActive = false;
  seasonOpen = false;
  activeSeasonRows.clear();
  seasonActiveAll = false;
  document.getElementById('season-panel').classList.remove('open');
  document.getElementById('season-toggle').classList.remove('active');
  clearRoute();
  showAll();
  setStatus('');
}}

// ── Core filter logic ──
let debounceTimer;

function onSearch() {{
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(applyFilters, 150);
}}

function applyFilters() {{
  // Close season panel
  if (seasonOpen) toggleSeason();

  const q     = document.getElementById('search').value.trim().toLowerCase();
  const fName = document.getElementById('f-name').value;
  const fGenus= document.getElementById('f-genus').value;
  const fAge  = document.getElementById('f-age').value;
  const fCond = document.getElementById('f-cond').value;

  document.getElementById('clear-btn').style.display = q ? 'block' : 'none';

  ['f-name','f-genus','f-age','f-cond'].forEach(id => {{
    const el = document.getElementById(id);
    el.classList.toggle('set', !!el.value);
  }});

  const activeCount = [fName, fGenus, fAge, fCond].filter(Boolean).length;
  const badge = document.getElementById('filter-badge');
  if (activeCount > 0) {{
    badge.textContent = activeCount;
    badge.style.display = 'inline';
    document.getElementById('filter-clear').style.display = 'block';
    document.getElementById('filter-toggle').classList.add('active');
  }} else {{
    badge.style.display = 'none';
    document.getElementById('filter-clear').style.display = 'none';
    if (!document.getElementById('filter-panel').classList.contains('open')) {{
      document.getElementById('filter-toggle').classList.remove('active');
    }}
  }}

  if (!q && !fName && !fGenus && !fAge && !fCond) {{
    showAll(); return;
  }}

  const matched = allMarkers.filter(m => {{
    const t = m._treeData;
    if (q     && !t.name.toLowerCase().includes(q)) return false;
    if (fName && t.name  !== fName)  return false;
    if (fGenus&& t.genus !== fGenus) return false;
    if (fAge  && t.age   !== fAge)   return false;
    if (fCond && t.cond  !== fCond)  return false;
    return true;
  }});

  layer.clearLayers();

  if (matched.length === 0) {{ setStatus('No trees found'); return; }}

  matched.forEach(m => {{
    m.setStyle({{ radius: 8, fillOpacity: 0.95, opacity: 1 }});
    layer.addLayer(m);
  }});

  const lats = matched.map(m => m._treeData.lat);
  const lngs = matched.map(m => m._treeData.lng);
  map.fitBounds(
    L.latLngBounds([Math.min(...lats), Math.min(...lngs)], [Math.max(...lats), Math.max(...lngs)]),
    {{ padding: [60, 60], maxZoom: 18 }}
  );

  const species = [...new Set(matched.map(m => m._treeData.name))];
  const label = species.length === 1
    ? `${{matched.length}} ${{species[0]}} on campus`
    : `${{matched.length}} trees across ${{species.length}} species`;
  setStatus(label);
}}

function showAll() {{
  layer.clearLayers();
  allMarkers.forEach(m => {{
    m.setStyle({{ radius: 5, fillOpacity: 0.75, opacity: 0.9, color: m._treeData.color, fillColor: m._treeData.color }});
    layer.addLayer(m);
  }});
  setStatus('');
}}

function clearAll() {{
  document.getElementById('search').value = '';
  document.getElementById('clear-btn').style.display = 'none';
  clearFilters();
}}

function clearFilters() {{
  ['f-name','f-genus','f-age','f-cond'].forEach(id => {{
    document.getElementById(id).value = '';
    document.getElementById(id).classList.remove('set');
  }});
  document.getElementById('filter-badge').style.display = 'none';
  document.getElementById('filter-clear').style.display = 'none';
  document.getElementById('filter-toggle').classList.remove('active');
  applyFilters();
}}

function setStatus(msg) {{
  const el = document.getElementById('status');
  if (msg) {{ el.textContent = msg; el.style.display = 'block'; }}
  else {{ el.style.display = 'none'; }}
}}

// ── Season panel ──────────────────────────────────────────────────────────────

let activeSeasonRows = new Set(); // species names currently highlighted on map
let seasonActiveAll = false;
let seasonOpen = false;

function getSelectedMMDD() {{
  const val = document.getElementById('season-date').value; // YYYY-MM-DD
  return val ? val.slice(5) : todayMMDD(); // MM-DD
}}

function renderSeasonPanel() {{
  const mmdd = getSelectedMMDD();
  const hits = getExcitingTrees(mmdd);

  // Group by event type
  const groups = {{}};
  const typeLabel = {{
    bloom:      '🌸 Blooming',
    fall_color: '🍂 Fall Color',
    foliage:    '🌿 Foliage Interest',
    fruit:      '🍎 Fruit Display',
    bark:       '🌳 Bark & Form',
    fragrance:  '✨ Fragrance',
  }};
  const typeOrder = ['bloom','fall_color','foliage','fruit','fragrance','bark'];

  hits.forEach(({{tree, events}}) => {{
    events.forEach(ev => {{
      if (!groups[ev.type]) groups[ev.type] = {{}};
      const key = tree.name;
      if (!groups[ev.type][key]) {{
        groups[ev.type][key] = {{ name: tree.name, ev, count: 0 }};
      }}
      groups[ev.type][key].count++;
    }});
  }});

  const list = document.getElementById('season-list');
  list.innerHTML = '';

  let totalSpecies = 0;
  typeOrder.forEach(type => {{
    if (!groups[type]) return;
    const entries = Object.values(groups[type]).sort((a,b) => b.count - a.count);
    totalSpecies += entries.length;

    const grp = document.createElement('div');
    grp.className = 'season-group';

    const hdr = document.createElement('div');
    hdr.className = 'season-group-header';
    hdr.textContent = typeLabel[type] || type;
    grp.appendChild(hdr);

    entries.forEach(entry => {{
      const row = document.createElement('div');
      row.className = 'season-species-row' + (activeSeasonRows.has(entry.name) ? ' active' : '');
      row.dataset.species = entry.name;
      row.innerHTML = `
        <div>
          <div class="season-species-name">${{entry.ev.icon}} ${{entry.name}}</div>
          <div class="season-species-sub">${{entry.ev.name}}</div>
        </div>
        <div class="season-species-count">${{entry.count}} tree${{entry.count!==1?'s':''}}</div>
      `;
      row.addEventListener('click', () => toggleSeasonSpecies(entry.name, type, row));
      grp.appendChild(row);
    }});

    list.appendChild(grp);
  }});

  if (totalSpecies === 0) {{
    list.innerHTML = '<div class="season-empty">No highlighted trees for this date.<br>Try a different date.</div>';
  }} else {{
    setStatus(`${{totalSpecies}} species with exciting moments today`);
  }}

  // Update map if "show all" is active
  if (seasonActiveAll) showAllInSeason();
}}

function toggleSeasonSpecies(speciesName, eventType, rowEl) {{
  if (activeSeasonRows.has(speciesName)) {{
    activeSeasonRows.delete(speciesName);
    rowEl.classList.remove('active');
  }} else {{
    activeSeasonRows.add(speciesName);
    rowEl.classList.add('active');
  }}
  seasonActiveAll = false;

  if (activeSeasonRows.size === 0) {{
    showAll();
    return;
  }}

  // Highlight selected species, dim others
  const mmdd = getSelectedMMDD();
  layer.clearLayers();
  const highlighted = [];

  allMarkers.forEach(m => {{
    const t = m._treeData;
    if (activeSeasonRows.has(t.name)) {{
      const evColor = (SEASONAL[t.name] || []).find(ev =>
        ev.type === eventType && dateInRange(mmdd, ev.start, ev.end)
      );
      const col = evColor ? (TYPE_COLOR[evColor.type] || t.color) : t.color;
      m.setStyle({{ radius: 9, fillColor: col, color: col, fillOpacity: 0.95, opacity: 1, weight: 2 }});
      layer.addLayer(m);
      highlighted.push(m);
    }} else {{
      m.setStyle({{ radius: 4, fillColor: '#ccc', color: '#aaa', fillOpacity: 0.4, opacity: 0.4, weight: 1 }});
      layer.addLayer(m);
    }}
  }});

  if (highlighted.length) {{
    const lats = highlighted.map(m => m._treeData.lat);
    const lngs = highlighted.map(m => m._treeData.lng);
    map.fitBounds(
      L.latLngBounds([Math.min(...lats), Math.min(...lngs)], [Math.max(...lats), Math.max(...lngs)]),
      {{ padding: [60, 60], maxZoom: 18 }}
    );
  }}
}}

function showAllInSeason() {{
  seasonActiveAll = true;
  activeSeasonRows.clear();
  // Update row styling
  document.querySelectorAll('.season-species-row').forEach(r => r.classList.remove('active'));

  const mmdd = getSelectedMMDD();
  const exciting = new Set(getExcitingTrees(mmdd).map(h => h.tree.name));

  layer.clearLayers();
  const highlighted = [];

  allMarkers.forEach(m => {{
    const t = m._treeData;
    if (exciting.has(t.name)) {{
      // Color by first active event type
      const activeEvs = (SEASONAL[t.name] || []).filter(ev => dateInRange(mmdd, ev.start, ev.end));
      const col = activeEvs.length ? (TYPE_COLOR[activeEvs[0].type] || t.color) : t.color;
      m.setStyle({{ radius: 8, fillColor: col, color: col, fillOpacity: 0.9, opacity: 1, weight: 2 }});
      layer.addLayer(m);
      highlighted.push(m);
    }} else {{
      m.setStyle({{ radius: 3, fillColor: '#ccc', color: '#aaa', fillOpacity: 0.3, opacity: 0.3, weight: 1 }});
      layer.addLayer(m);
    }}
  }});

  if (highlighted.length) {{
    const lats = highlighted.map(m => m._treeData.lat);
    const lngs = highlighted.map(m => m._treeData.lng);
    map.fitBounds(
      L.latLngBounds([Math.min(...lats), Math.min(...lngs)], [Math.max(...lats), Math.max(...lngs)]),
      {{ padding: [60, 60], maxZoom: 19 }}
    );
  }}

  setStatus(`${{highlighted.length}} trees with exciting moments`);
}}

// ── Walking route ─────────────────────────────────────────────────────────────

let routingControl = null;

const MAIN_GATE = [41.6866, -73.8955]; // Raymond Ave main entrance

function nearestNeighbor(points, start) {{
  // Greedy TSP: always go to the closest unvisited point
  const remaining = [...points];
  const path = [];
  let cur = start;
  while (remaining.length > 0) {{
    let best = -1, bestDist = Infinity;
    remaining.forEach((p, i) => {{
      const d = Math.pow(p[0]-cur[0],2) + Math.pow(p[1]-cur[1],2);
      if (d < bestDist) {{ bestDist = d; best = i; }}
    }});
    path.push(remaining[best]);
    cur = remaining[best];
    remaining.splice(best, 1);
  }}
  return path;
}}

function clusterWaypoints(points, radiusDeg) {{
  // Single-pass greedy spatial clustering.
  // Trees within radiusDeg (~100m) of each other become one "area stop".
  // Returns array of {{ lat, lng, count }} cluster centroids.
  const assigned = new Array(points.length).fill(false);
  const clusters = [];
  for (let i = 0; i < points.length; i++) {{
    if (assigned[i]) continue;
    const members = [i];
    assigned[i] = true;
    for (let j = i + 1; j < points.length; j++) {{
      if (assigned[j]) continue;
      const d = Math.sqrt(Math.pow(points[i][0]-points[j][0],2) + Math.pow(points[i][1]-points[j][1],2));
      if (d < radiusDeg) {{ members.push(j); assigned[j] = true; }}
    }}
    const lat = members.reduce((s,k) => s + points[k][0], 0) / members.length;
    const lng = members.reduce((s,k) => s + points[k][1], 0) / members.length;
    clusters.push({{ lat, lng, count: members.length }});
  }}
  return clusters;
}}

function buildWalkRoute() {{
  clearRoute();

  const mmdd = getSelectedMMDD();
  let excitingMarkers = getExcitingTrees(mmdd).map(h => h.marker);

  // Filter to species currently highlighted
  if (activeSeasonRows.size > 0) {{
    excitingMarkers = excitingMarkers.filter(m => activeSeasonRows.has(m._treeData.name));
  }}

  if (excitingMarkers.length === 0) {{
    document.getElementById('route-info').style.display = 'block';
    document.getElementById('route-info').textContent = 'No exciting trees to route to. Show trees first.';
    return;
  }}

  const startPt = window._userLoc || MAIN_GATE;

  // Cluster trees within ~100m of each other into area stops.
  // This gives a realistic "rough tour through areas" rather than zigzagging
  // to every individual tree on a lawn.
  const allPoints = excitingMarkers.map(m => [m._treeData.lat, m._treeData.lng]);
  let clusters = clusterWaypoints(allPoints, 0.0009); // 0.0009° ≈ 100m

  // Prefer larger clusters (more trees per stop), cap at 12
  clusters.sort((a, b) => b.count - a.count);
  clusters = clusters.slice(0, 12);

  const totalTrees = excitingMarkers.length;
  let waypoints = clusters.map(c => [c.lat, c.lng]);

  // Order waypoints with nearest-neighbor heuristic
  const ordered = nearestNeighbor(waypoints, startPt);
  // Attach tree counts to ordered stops for the info message
  const orderedClusters = ordered.map(pt => clusters.find(c => c.lat === pt[0] && c.lng === pt[1]) || {{ count: 1 }});
  const allWaypoints = [startPt, ...ordered];

  const lrWaypoints = allWaypoints.map(p => L.latLng(p[0], p[1]));

  routingControl = L.Routing.control({{
    waypoints: lrWaypoints,
    router: L.Routing.osrmv1({{
      serviceUrl: 'https://routing.openstreetmap.de/routed-foot/route/v1',
    }}),
    lineOptions: {{
      styles: [{{ color: '#1565c0', weight: 4, opacity: 0.8 }}],
      extendToWaypoints: false,
      missingRouteTolerance: 0,
    }},
    addWaypoints: false,
    draggableWaypoints: false,
    fitSelectedRoutes: true,
    show: false, // hide the routing panel
    createMarker: () => null, // suppress default markers
  }}).addTo(map);

  routingControl.on('routesfound', e => {{
    const route = e.routes[0];
    const dist = (route.summary.totalDistance / 1000).toFixed(2);
    const mins = Math.round(route.summary.totalTime / 60);
    const info = document.getElementById('route-info');
    info.style.display = 'block';
    const coveredTrees = orderedClusters.reduce((s, c) => s + c.count, 0);
    info.textContent = `🚶 ${{dist}} km · ~${{mins}} min · ${{ordered.length}} stops · ${{coveredTrees}}/${{totalTrees}} trees`;

    document.getElementById('clear-route-btn').style.display = 'block';
  }});

  routingControl.on('routingerror', () => {{
    const info = document.getElementById('route-info');
    info.style.display = 'block';
    info.textContent = 'Could not compute route — check your internet connection.';
  }});
}}

function clearRoute() {{
  if (routingControl) {{
    map.removeControl(routingControl);
    routingControl = null;
  }}
  document.getElementById('route-info').style.display = 'none';
  document.getElementById('clear-route-btn').style.display = 'none';
}}

// Geolocation
let locMarker = null;
function locateMe() {{
  if (!navigator.geolocation) {{ alert('Geolocation not supported'); return; }}
  navigator.geolocation.getCurrentPosition(pos => {{
    const ll = [pos.coords.latitude, pos.coords.longitude];
    window._userLoc = ll;
    if (locMarker) map.removeLayer(locMarker);
    locMarker = L.circleMarker(ll, {{
      radius: 8, color: '#1565c0', fillColor: '#1e88e5',
      fillOpacity: 0.9, weight: 2
    }}).addTo(map).bindPopup('You are here').openPopup();
    map.setView(ll, 18);
  }}, err => {{
    const msg = {{1:'Permission denied — allow location in browser settings',
                 2:'Position unavailable',
                 3:'Request timed out'}}[err.code] || 'Unknown error';
    alert('Location failed: ' + msg);
  }});
}}

document.getElementById('search').addEventListener('input', onSearch);
showAll();
</script>
</body>
</html>"""

with open('vassar-tree-map.html', 'w') as f:
    f.write(html)

with open('index.html', 'w') as f:
    f.write(html)

print(f"Done. {len(trees)} trees, {len(seasonal)} species with seasonal data.")
print(f"Output: vassar-tree-map.html ({len(html)//1024} KB)")

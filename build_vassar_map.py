import csv, json
from collections import Counter

# Read enriched data
enriched = json.load(open('vassar_enriched.json'))

# Read tree data
trees = []
with open('vassar_arboretum.csv') as f:
    for row in csv.DictReader(f):
        bid = row['bartlett_id']
        extra = enriched.get(bid, {})
        genus = row['genus'].strip()
        trees.append({
            'id': int(row['internal_id']),
            'bid': bid,
            'name': row['common_name'],
            'genus': genus,
            'sci': extra.get('sci', ''),
            'age': extra.get('age', ''),
            'cond': extra.get('cond', ''),
            'lat': float(row['latitude']),
            'lng': float(row['longitude']),
            'color': '#' + row['color_code']
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

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>Vassar Arboretum</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
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
  width: min(440px, calc(100vw - 24px));
}}

#search-wrap {{
  display: flex;
  align-items: center;
  background: rgba(255,255,255,0.97);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.25);
  padding: 10px 14px;
  gap: 8px;
}}

#search {{
  flex: 1;
  border: none;
  outline: none;
  font-size: 17px;
  background: transparent;
  color: #111;
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
}}

/* Filter toggle button */
#filter-toggle {{
  display: flex;
  align-items: center;
  gap: 5px;
  background: none;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  padding: 4px 10px;
  font-size: 13px;
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
</style>
</head>
<body>

<div id="map"></div>

<div id="ui">

  <!-- Search row -->
  <div id="search-wrap">
    <span style="font-size:18px;color:#888">🔍</span>
    <input id="search" type="search" placeholder="Search trees…" autocomplete="off" autocorrect="off" spellcheck="false">
    <button id="clear-btn" onclick="clearAll()">×</button>
    <button id="filter-toggle" onclick="toggleFilters()">
      ⚙ Browse <span id="filter-badge"></span>
    </button>
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

  <div id="status"></div>
</div>

<button id="locate-btn" onclick="locateMe()" title="My location">📍</button>

<script>
const TREES = {trees_json};

// Map
const map = L.map('map', {{ center: [41.6873, -73.8966], zoom: 16, zoomControl: true }});
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  attribution: '© OpenStreetMap contributors', maxZoom: 20
}}).addTo(map);

const layer = L.layerGroup().addTo(map);

const allMarkers = TREES.map(t => {{
  const m = L.circleMarker([t.lat, t.lng], {{
    radius: 5, color: t.color, fillColor: t.color,
    fillOpacity: 0.75, weight: 1.2, opacity: 0.9
  }});
  const ageRow  = t.age  ? `<div class="pp-row"><span class="pp-lbl">Age Class:</span> ${{t.age}}</div>`  : '';
  const condRow = t.cond ? `<div class="pp-row"><span class="pp-lbl">Condition Class:</span> ${{t.cond}}</div>` : '';
  m.bindPopup(
    `<div class="pp-id">Tree ID: ${{t.id}}</div>` +
    `<div class="pp-name">${{t.name}}</div>` +
    `<div class="pp-sci">${{t.sci || t.genus}}</div>` +
    ageRow + condRow,
    {{ maxWidth: 240 }}
  );
  m._treeData = t;
  return m;
}});

// ── Filter panel toggle ──
function toggleFilters() {{
  const panel = document.getElementById('filter-panel');
  const btn   = document.getElementById('filter-toggle');
  panel.classList.toggle('open');
  btn.classList.toggle('active');
}}

// ── Core filter logic ──
let debounceTimer;

function onSearch() {{
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(applyFilters, 150);
}}

function applyFilters() {{
  const q     = document.getElementById('search').value.trim().toLowerCase();
  const fName = document.getElementById('f-name').value;
  const fGenus= document.getElementById('f-genus').value;
  const fAge  = document.getElementById('f-age').value;
  const fCond = document.getElementById('f-cond').value;

  // Show/hide clear button for text search
  document.getElementById('clear-btn').style.display = q ? 'block' : 'none';

  // Style dropdowns that are set
  ['f-name','f-genus','f-age','f-cond'].forEach(id => {{
    const el = document.getElementById(id);
    el.classList.toggle('set', !!el.value);
  }});

  // Count active filters (excluding text search)
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

  // Nothing active — show all
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

  // Fly to fit
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
    m.setStyle({{ radius: 5, fillOpacity: 0.75, opacity: 0.9 }});
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

// Geolocation
let locMarker = null;
function locateMe() {{
  if (!navigator.geolocation) {{ alert('Geolocation not supported'); return; }}
  navigator.geolocation.getCurrentPosition(pos => {{
    const ll = [pos.coords.latitude, pos.coords.longitude];
    if (locMarker) map.removeLayer(locMarker);
    locMarker = L.circleMarker(ll, {{
      radius: 8, color: '#1565c0', fillColor: '#1e88e5',
      fillOpacity: 0.9, weight: 2
    }}).addTo(map).bindPopup('You are here').openPopup();
    map.setView(ll, 18);
  }}, () => alert('Could not get location'));
}}

document.getElementById('search').addEventListener('input', onSearch);
showAll();
</script>
</body>
</html>"""

with open('vassar-tree-map.html', 'w') as f:
    f.write(html)

print(f"Done. {len(trees)} trees. Output: vassar-tree-map.html ({len(html)//1024} KB)")

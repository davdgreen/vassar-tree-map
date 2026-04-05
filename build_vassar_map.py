import csv, json

# Read enriched data
enriched = json.load(open('vassar_enriched.json'))

# Read tree data
trees = []
with open('vassar_arboretum.csv') as f:
    for row in csv.DictReader(f):
        bid = row['bartlett_id']
        extra = enriched.get(bid, {})
        trees.append({
            'id': int(row['internal_id']),
            'bid': bid,
            'name': row['common_name'],
            'sci': extra.get('sci', ''),
            'age': extra.get('age', ''),
            'cond': extra.get('cond', ''),
            'lat': float(row['latitude']),
            'lng': float(row['longitude']),
            'color': '#' + row['color_code']
        })

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

#ui {{
  position: absolute;
  top: 12px; left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  width: min(420px, calc(100vw - 24px));
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

.pp-id   {{ font-size: 12px; color: #666; margin-bottom: 3px; }}
.pp-name {{ font-size: 15px; font-weight: 600; color: #111; margin-bottom: 2px; }}
.pp-sci  {{ font-size: 13px; font-style: italic; color: #444; margin-bottom: 6px; }}
.pp-row  {{ font-size: 12px; color: #333; margin-top: 3px; }}
.pp-lbl  {{ color: #666; }}

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
  <div id="search-wrap">
    <span style="font-size:18px;color:#888">🔍</span>
    <input id="search" type="search" placeholder="Search trees… (e.g. Dawn Redwood)" autocomplete="off" autocorrect="off" spellcheck="false">
    <button id="clear-btn" onclick="clearSearch()">×</button>
  </div>
  <div id="status"></div>
</div>

<button id="locate-btn" onclick="locateMe()" title="My location">📍</button>

<script>
const TREES = {trees_json};

// Map setup
const map = L.map('map', {{
  center: [41.6873, -73.8966],
  zoom: 16,
  zoomControl: true
}});

L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  attribution: '© OpenStreetMap contributors',
  maxZoom: 20
}}).addTo(map);

// Layer group for tree markers
const layer = L.layerGroup().addTo(map);

// Build all markers once, reuse
const allMarkers = TREES.map(t => {{
  const m = L.circleMarker([t.lat, t.lng], {{
    radius: 5,
    color: t.color,
    fillColor: t.color,
    fillOpacity: 0.75,
    weight: 1.2,
    opacity: 0.9
  }});
  const ageRow  = t.age  ? `<div class="pp-row"><span class="pp-lbl">Age Class:</span> ${{t.age}}</div>`  : '';
  const condRow = t.cond ? `<div class="pp-row"><span class="pp-lbl">Condition Class:</span> ${{t.cond}}</div>` : '';
  m.bindPopup(
    `<div class="pp-id">Tree ID: ${{t.id}}</div>` +
    `<div class="pp-name">${{t.name}}</div>` +
    `<div class="pp-sci">${{t.sci || t.genus}}</div>` +
    ageRow + condRow,
    {{maxWidth: 240}}
  );
  m._treeData = t;
  return m;
}});

// Show all on load
function showAll() {{
  layer.clearLayers();
  allMarkers.forEach(m => {{
    m.setStyle({{ radius: 5, fillOpacity: 0.75, opacity: 0.9 }});
    layer.addLayer(m);
  }});
  setStatus('');
}}

// Filter markers
let debounceTimer;
function onSearch() {{
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(applySearch, 150);
}}

function applySearch() {{
  const q = document.getElementById('search').value.trim().toLowerCase();
  document.getElementById('clear-btn').style.display = q ? 'block' : 'none';

  if (!q) {{ showAll(); return; }}

  const matched = allMarkers.filter(m => m._treeData.name.toLowerCase().includes(q));

  layer.clearLayers();

  if (matched.length === 0) {{
    setStatus('No trees found');
    return;
  }}

  // Distinct species in results
  const species = [...new Set(matched.map(m => m._treeData.name))];

  matched.forEach(m => {{
    m.setStyle({{ radius: 8, fillOpacity: 0.95, opacity: 1 }});
    layer.addLayer(m);
  }});

  // Fly to fit all matched markers
  const lats = matched.map(m => m._treeData.lat);
  const lngs = matched.map(m => m._treeData.lng);
  const bounds = L.latLngBounds(
    [Math.min(...lats), Math.min(...lngs)],
    [Math.max(...lats), Math.max(...lngs)]
  );
  map.fitBounds(bounds, {{ padding: [60, 60], maxZoom: 18 }});

  const label = species.length === 1
    ? `${{matched.length}} ${{species[0]}} on campus`
    : `${{matched.length}} trees across ${{species.length}} species`;
  setStatus(label);
}}

function clearSearch() {{
  document.getElementById('search').value = '';
  document.getElementById('clear-btn').style.display = 'none';
  showAll();
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

// Init
document.getElementById('search').addEventListener('input', onSearch);
showAll();
</script>
</body>
</html>"""

with open('vassar-tree-map.html', 'w') as f:
    f.write(html)

print(f"Done. {len(trees)} trees. Output: vassar-tree-map.html ({len(html)//1024} KB)")

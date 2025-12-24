import json
import os
from os.path import dirname, realpath, join
from shapely.geometry import shape, mapping

SCRIPT_DIR = dirname(realpath(__file__))
INPUT_FILE =  join(SCRIPT_DIR, 'geojson_br.json')
OUTPUT_FILE =  join(SCRIPT_DIR, 'geojson_br_optimized.json')

print(f'Reading {INPUT_FILE}...')
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Simplifying shapes... (This can take a while...)")
new_features = []

for feature in data['features']:

    # Removing useless properties from the original GEOJSON
    properties = {
        'id': feature['properties']['id'],
        'name': feature['properties'].get('name', '')
    }
    
    geom = shape(feature['geometry'])
    simplified = geom.simplify(0.01, preserve_topology=True)
    
    new_features.append({
        'type': 'Feature',
        'properties': properties,
        'geometry': mapping(simplified)
    })

data['features'] = new_features

print(f'Saving {OUTPUT_FILE}...')
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f)

# Size comparison
size_old = os.path.getsize(INPUT_FILE) / (1024*1024)
size_new = os.path.getsize(OUTPUT_FILE) / (1024*1024)
print(f'Success! Reduced size: {size_old:.2f} MB to {size_new:.2f} MB')
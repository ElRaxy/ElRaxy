"""Set an intrinsic 28 px height on existing local vector badges, preserving art."""
import json
from pathlib import Path
import re
from xml.etree import ElementTree

root = Path(__file__).resolve().parents[1]
manifest = root / 'assets-src/profile-badges.json'
data = json.loads(manifest.read_text())
for asset in data['assets']:
    path = root / asset['path']
    svg = path.read_text()
    node = ElementTree.fromstring(svg)
    box = node.get('viewBox', f"0 0 {node.get('width')} {node.get('height')}")
    _, _, width, height = map(float, box.split())
    head = re.search(r'<svg\b[^>]*>', svg).group()
    resized = re.sub(r'\bwidth="[^"]+"', f'width="{width * 28 / height:g}"', head)
    resized = re.sub(r'\bheight="[^"]+"', 'height="28"', resized)
    if 'viewBox=' not in resized:
        resized = resized[:-1] + f' viewBox="{box}">'
    path.write_text(svg.replace(head, resized, 1))
data['display_height'] = 28
manifest.write_text(json.dumps(data, indent=2) + '\n')

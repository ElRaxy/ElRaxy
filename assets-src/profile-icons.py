"""Original blue pictograms for the GitHub profile. No fonts or external assets."""
from pathlib import Path

SHAPES = {
    'about': '<circle cx="12" cy="8" r="3"/><path d="M5 20v-2a7 7 0 0 1 14 0v2"/>',
    'code': '<rect x="2" y="3" width="20" height="18" rx="3"/><path d="m8 10-3 3 3 3m8-6 3 3-3 3m-3-7-2 10"/>',
    'tools': '<path d="m5 7 4 4-4 4m7 2h7"/><rect x="2" y="3" width="20" height="18" rx="3"/>',
    'video': '<rect x="2" y="4" width="20" height="16" rx="3"/><path d="m10 8 6 4-6 4Z"/>',
    'shield': '<path d="m12 2 8 3v6c0 5-4 8-8 11-4-3-8-6-8-11V5Z"/><path d="m8 12 3 3 5-6"/>',
    'projects': '<rect x="2" y="3" width="8" height="8" rx="2"/><rect x="14" y="3" width="8" height="8" rx="2"/><rect x="2" y="15" width="8" height="7" rx="2"/><path d="M14 18h8m-4-4v8"/>',
    'metrics': '<path d="M3 3v18h19M7 15v3m5-8v8m5-13v13"/>',
}
root = Path(__file__).resolve().parents[1] / 'assets' / 'profile'
for name, shape in SHAPES.items():
    (root / f'icon-{name}.svg').write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
        '<g fill="none" stroke="#4d71ff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        + shape + '</g></svg>\n'
    )

import json
from pathlib import Path
import collections

opt_dir = Path("optimized")
base_url = "https://cdn.jsdelivr.net/gh/vanshdigitals/Vanshdigitals-Assets@main/optimized"

data = collections.defaultdict(lambda: collections.defaultdict(list))

# Ensure natural sorting by sorting the strings
files = sorted(opt_dir.glob("Builders-Playground/**/*.webp"), key=lambda p: (p.parent, p.stem.zfill(10)))

for f in files:
    rel_path = f.relative_to(opt_dir)
    brand = rel_path.parts[0]
    carousel = rel_path.parts[1]
    url = f"{base_url}/{brand}/{carousel}/{f.name}"
    data["builders-playground"][carousel].append(url)

# Print total counts per folder
print("COUNTS:")
for carousel, urls in data["builders-playground"].items():
    print(f"  {carousel}: {len(urls)} images")

print("---JSON_START---")
print(json.dumps(data, indent=2))

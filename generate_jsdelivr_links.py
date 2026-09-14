import json
import re
from pathlib import Path
import collections

opt_dir = Path("optimized")
base_url = "https://cdn.jsdelivr.net/gh/vanshdigitals/Vanshdigitals-Assets@main/optimized"

def natural_sort_key(p):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', str(p))]

target_dir = opt_dir / "Keshvi-Beauty-Lounge"
files = sorted(target_dir.rglob("*.webp"), key=natural_sort_key)

data = collections.defaultdict(lambda: collections.defaultdict(list))

name_mapping = {
    "Carousel/KBL-Carousel-1-TextureVsCakey-Bridal-Authority": "Carousel 1 - TextureVsCakey Bridal Authority",
    "Carousel/KBL-Carousel-2-PartyGlam-Portfolio": "Carousel 2 - PartyGlam Portfolio",
    "Carousel/KBL-Carousel-3-Heritage-Bride-Portfolio": "Carousel 3 - Heritage Bride Portfolio",
    "KBL-Signature-Packages-Collection-Posters": "Posters - Signature Packages Collection",
    "Keshvi-Beauty-Lounge-Logo": "Logo",
    "Reel-Cover": "Reel Cover - Mehendi Portfolio"
}

for f in files:
    rel_path = f.relative_to(opt_dir)
    brand = rel_path.parts[0]
    
    if len(rel_path.parts) > 2:
        subfolder_path = "/".join(rel_path.parts[1:-1])
    else:
        subfolder_path = rel_path.parts[1]
    
    human_name = name_mapping.get(subfolder_path, subfolder_path)
    
    url_path = "/".join(rel_path.parts)
    url = f"{base_url}/{url_path}"
    data[brand][human_name].append(url)

md_lines = []
md_lines.append("# jsDelivr Asset Links\n")

for brand, subfolders in data.items():
    md_lines.append(f"## {brand}\n")
    for subfolder, urls in subfolders.items():
        header_name = subfolder.replace(" - ", " — ")
        count = len(urls)
        img_word = "image" if count == 1 else "images"
        md_lines.append(f"### {header_name}  ({count} {img_word})\n")
        for url in urls:
            md_lines.append(url)
        md_lines.append("")

md_lines.append("\n## JSON Data\n")
md_lines.append("```json")
md_lines.append(json.dumps(data, indent=2))
md_lines.append("```")

with open("jsdelivr-links.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print("Updated jsdelivr-links.md successfully.")

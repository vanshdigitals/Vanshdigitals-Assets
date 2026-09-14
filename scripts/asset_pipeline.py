"""
DESIGN WORK GALLERY — Asset Pipeline & Direct jsDelivr Link Generator

1. Scans source designs in originals/ (never modified).
2. Converts PNG -> WebP with high visual fidelity, preserved dimensions, and transparency.
3. Organizes assets into predictable brand/category/project structures.
4. Generates direct jsDelivr CDN URLs:
   https://cdn.jsdelivr.net/gh/vanshdigitals/Vanshdigitals-Assets@main/optimized/...
5. Generates copy-paste-ready jsdelivr-links.md.
6. Generates machine-readable design-assets.json.
7. Validates assets integrity, serial orders, and URLs.
"""

import io
import json
import math
import os
import re
import sys
import zipfile
from fractions import Fraction
from pathlib import Path
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "originals"
OPT_DIR = REPO_ROOT / "optimized"
BASE_URL = "https://cdn.jsdelivr.net/gh/vanshdigitals/Vanshdigitals-Assets@main/optimized"

WEBP_QUALITY = 90
WEBP_METHOD = 6

def natural_sort_key(s):
    """Sort strings containing numbers in natural human order (e.g. 2 comes before 10)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

def calculate_aspect_ratio(width: int, height: int) -> str:
    """Return standard aspect ratio string (e.g. '4:5', '9:16', '1:1', '3:4', '16:9')."""
    if height == 0:
        return "1:1"
    ratio = width / height
    common_ratios = [
        (1.0, "1:1"),
        (4 / 5, "4:5"),
        (5 / 4, "5:4"),
        (9 / 16, "9:16"),
        (16 / 9, "16:9"),
        (3 / 4, "3:4"),
        (4 / 3, "4:3"),
        (2 / 3, "2:3"),
        (3 / 2, "3:2"),
        (1 / math.sqrt(2), "1:1.41"),
    ]
    for target, label in common_ratios:
        if abs(ratio - target) < 0.035:
            return label
    divisor = math.gcd(width, height)
    if divisor > 10:
        return f"{width // divisor}:{height // divisor}"
    return f"{ratio:.2f}:1"

def convert_to_webp(image_data, dest_path: Path) -> dict:
    """Convert image bytes or file to WebP and save, returning metadata."""
    if isinstance(image_data, (str, Path)):
        img = Image.open(image_data)
    else:
        img = Image.open(io.BytesIO(image_data))
    
    width, height = img.size
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    img = img.convert("RGBA") if has_alpha else img.convert("RGB")
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest_path, format="WEBP", quality=WEBP_QUALITY, method=WEBP_METHOD)
    
    size_bytes = dest_path.stat().st_size
    return {
        "width": width,
        "height": height,
        "aspectRatio": calculate_aspect_ratio(width, height),
        "sizeBytes": size_bytes,
        "format": "webp"
    }

def clean_project_name(name: str) -> str:
    """Normalize project name into predictable slug with preserved identifiers."""
    name = re.sub(r'00(\d)', r'0\1', name)  # e.g., RR 001 -> RR 01
    name = name.replace("'", "")
    name = name.replace("!", "")
    name = name.replace("?", "")
    name = name.replace("&", "and")
    name = re.sub(r'[\s_]+', '-', name)
    name = re.sub(r'-+', '-', name).strip('-')
    return name

def format_title_from_slug(slug: str) -> str:
    """Convert slug into clean, readable title matching user format (e.g. RR-01 — Title)."""
    match = re.match(r'^(RR-\d+|CC-Dark-\d+|CC-Light-\d+|CC-Light-Part2-\d+|WP-\d+|KBL-Carousel-\d+)-(.*)$', slug, re.I)
    acronyms = {
        "ai": "AI",
        "chatgpt": "ChatGPT",
        "3d": "3D",
        "partyglam": "PartyGlam",
        "texturevscakey": "TextureVsCakey",
        "bts": "BTS"
    }
    if match:
        prefix, rest = match.groups()
        words = rest.split("-")
        clean_words = []
        for w in words:
            low = w.lower()
            if low in acronyms:
                clean_words.append(acronyms[low])
            elif low in ("and", "vs", "the", "a", "an", "is", "of", "to", "for", "in", "on", "not", "or"):
                clean_words.append(low)
            elif low == "wont":
                clean_words.append("Won't")
            elif low == "isnt":
                clean_words.append("Isn't")
            elif low == "dont":
                clean_words.append("Don't")
            elif re.match(r'^\d+$', w):
                clean_words.append(w)
            else:
                clean_words.append(w.capitalize())
        clean_prefix = prefix.replace("Part2", "Part 2")
        return f"{clean_prefix} — {' '.join(clean_words)}"
    
    words = slug.split("-")
    return " ".join(acronyms.get(w.lower(), w.capitalize()) for w in words)

def process_ranjeet_raj():
    print("Processing RanjeetRaj...")
    brand_src = SRC_DIR / "RanjeetRaj"
    if not brand_src.exists():
        print("  Source RanjeetRaj not found, skipping.")
        return
    
    brand_opt = OPT_DIR / "RanjeetRaj" / "Carousel"
    projects = sorted([d for d in brand_src.iterdir() if d.is_dir()], key=lambda d: natural_sort_key(d.name))
    
    for p in projects:
        proj_slug = clean_project_name(p.name)
        dest_dir = brand_opt / proj_slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        pngs = sorted([f for f in p.glob("*.png")], key=lambda f: natural_sort_key(f.name))
        for idx, png_file in enumerate(pngs, start=1):
            out_file = dest_dir / f"{idx}.webp"
            convert_to_webp(png_file, out_file)
        print(f"  [RanjeetRaj] {proj_slug}: {len(pngs)} slides -> WebP")

def process_waterplane():
    print("Processing WaterPlane...")
    brand_src = SRC_DIR / "WaterPlane" / "Carausal"
    if not brand_src.exists():
        print("  Source WaterPlane not found, skipping.")
        return
    
    brand_opt = OPT_DIR / "WaterPlane" / "Carousel"
    projects = sorted([d for d in brand_src.iterdir() if d.is_dir()], key=lambda d: natural_sort_key(d.name))
    
    for p in projects:
        proj_slug = clean_project_name(p.name)
        dest_dir = brand_opt / proj_slug
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        pngs = sorted([f for f in p.glob("*.png")], key=lambda f: natural_sort_key(f.name))
        for idx, png_file in enumerate(pngs, start=1):
            out_file = dest_dir / f"{idx}.webp"
            convert_to_webp(png_file, out_file)
        print(f"  [WaterPlane] {proj_slug}: {len(pngs)} slides -> WebP")

def process_cuts_and_curves():
    print("Processing Cuts-and-Curves...")
    cc_src = SRC_DIR / "Cuts And Curves"
    if not cc_src.exists():
        print("  Source Cuts And Curves not found, skipping.")
        return
    
    brand_opt = OPT_DIR / "Cuts-and-Curves"
    
    # 1. Dark Themed Carousels
    dark_carousels_dir = cc_src / "Dark Themed" / "Carausals"
    if dark_carousels_dir.exists():
        dirs = sorted([d for d in dark_carousels_dir.iterdir() if d.is_dir()], key=lambda d: natural_sort_key(d.name))
        for d in dirs:
            proj_name = d.name
            # e.g. CC 01 5 BRIDAL SKINCARE MISTAKES -> CC-Dark-01-5-Bridal-Skincare-Mistakes
            clean_name = clean_project_name(proj_name).replace("CC-", "CC-Dark-")
            dest = brand_opt / "Carousel" / clean_name
            pngs = sorted([f for f in d.glob("*.png")], key=lambda f: natural_sort_key(f.name))
            for idx, f in enumerate(pngs, start=1):
                convert_to_webp(f, dest / f"{idx}.webp")
            print(f"  [Cuts-and-Curves] {clean_name}: {len(pngs)} slides")

    # Dark Themed Sample Carousel
    sample_zip = cc_src / "Dark Themed" / "Sample Carausal" / "ULTIMATE GLOW PACKAGE.zip"
    if sample_zip.exists():
        clean_name = "CC-Dark-11-Sample-Carousel-Ultimate-Glow-Package"
        dest = brand_opt / "Carousel" / clean_name
        with zipfile.ZipFile(sample_zip, 'r') as zf:
            png_names = sorted([n for n in zf.namelist() if n.lower().endswith(".png")], key=natural_sort_key)
            for idx, name in enumerate(png_names, start=1):
                convert_to_webp(zf.read(name), dest / f"{idx}.webp")
        print(f"  [Cuts-and-Curves] {clean_name}: {len(png_names)} slides")

    # 2. Light Themed Carousels (zip packages CC 01 to CC 12)
    light_dir = cc_src / "Light Themed" / "Carausal"
    if light_dir.exists():
        zips = sorted([z for z in light_dir.glob("*.zip")], key=lambda z: natural_sort_key(z.name))
        for z in zips:
            proj_stem = z.stem
            clean_name = clean_project_name(proj_stem).replace("CC-", "CC-Light-")
            dest = brand_opt / "Carousel" / clean_name
            with zipfile.ZipFile(z, 'r') as zf:
                png_names = sorted([n for n in zf.namelist() if n.lower().endswith(".png")], key=natural_sort_key)
                for idx, name in enumerate(png_names, start=1):
                    convert_to_webp(zf.read(name), dest / f"{idx}.webp")
            print(f"  [Cuts-and-Curves] {clean_name}: {len(png_names)} slides")

    # 3. Light Themed Part 2 Carousels (zip packages CC 01 to CC 12)
    light2_dir = cc_src / "Light Themed Part 2"
    if light2_dir.exists():
        zips = sorted([z for z in light2_dir.glob("*.zip")], key=lambda z: natural_sort_key(z.name))
        for z in zips:
            proj_stem = z.stem
            clean_name = clean_project_name(proj_stem).replace("CC-", "CC-Light-Part2-")
            dest = brand_opt / "Carousel" / clean_name
            with zipfile.ZipFile(z, 'r') as zf:
                png_names = sorted([n for n in zf.namelist() if n.lower().endswith(".png")], key=natural_sort_key)
                for idx, name in enumerate(png_names, start=1):
                    convert_to_webp(zf.read(name), dest / f"{idx}.webp")
            print(f"  [Cuts-and-Curves] {clean_name}: {len(png_names)} slides")

    # 4. Reel Covers
    # Term 02 (12-15) + Term 01 (16-45)
    reel_covers = []
    term02_dir = cc_src / "Dark Themed" / "Reel Cover" / "Insta Reel Cover Cuts & Curves Term 02"
    term01_dir = cc_src / "Dark Themed" / "Reel Cover" / "Insta Reel Cover Cuts & Curves Term 01"
    
    if term02_dir.exists():
        for f in term02_dir.glob("*.png"):
            reel_covers.append(f)
    if term01_dir.exists():
        for f in term01_dir.glob("*.png"):
            reel_covers.append(f)
            
    reel_covers = sorted(reel_covers, key=lambda f: natural_sort_key(f.name))
    reel_dest = brand_opt / "Reel-Cover"
    for idx, f in enumerate(reel_covers, start=1):
        convert_to_webp(f, reel_dest / f"{idx}.webp")
    print(f"  [Cuts-and-Curves] Reel Covers: {len(reel_covers)} covers -> WebP")

    # 5. Posts & Posters
    posters = []
    poster_pkg = cc_src / "Poster Package" / "POSTERS PACKAGE.zip"
    if poster_pkg.exists():
        with zipfile.ZipFile(poster_pkg, 'r') as zf:
            names = sorted([n for n in zf.namelist() if n.lower().endswith(".png")], key=natural_sort_key)
            for n in names:
                posters.append(("zip", poster_pkg, n))
                
    glow_png = cc_src / "Poster Package" / "ULTIMATE GLOW PACKAGE.png"
    if glow_png.exists():
        posters.append(("file", glow_png, glow_png.name))
        
    story_zip = cc_src / "Dark Themed" / "Story Static Design.zip"
    if story_zip.exists():
        with zipfile.ZipFile(story_zip, 'r') as zf:
            names = sorted([n for n in zf.namelist() if n.lower().endswith(".png")], key=natural_sort_key)
            for n in names:
                posters.append(("zip", story_zip, n))
                
    post_dest = brand_opt / "Post"
    for idx, item in enumerate(posters, start=1):
        if item[0] == "file":
            convert_to_webp(item[1], post_dest / f"{idx}.webp")
        else:
            with zipfile.ZipFile(item[1], 'r') as zf:
                convert_to_webp(zf.read(item[2]), post_dest / f"{idx}.webp")
    print(f"  [Cuts-and-Curves] Posts/Posters: {len(posters)} posts -> WebP")

def build_asset_catalog():
    """Inspect the entire optimized/ directory and build full catalog with metadata."""
    catalog = {}
    
    # Process each brand directory in optimized/
    brand_dirs = sorted([d for d in OPT_DIR.iterdir() if d.is_dir()], key=lambda d: d.name)
    
    for b in brand_dirs:
        brand_name = b.name
        # Skip legacy un-categorized folders if present
        catalog[brand_name] = {
            "carousel": {},
            "reelCover": [],
            "post": [],
            "logo": [],
            "highlights": []
        }
        
        # 1. Carousels
        carousel_dir = b / "Carousel"
        if not carousel_dir.exists():
            # Check for alternative name like Event-Carousel
            alt_carousel = b / "Event-Carousel"
            if alt_carousel.exists():
                webps = sorted([f for f in alt_carousel.glob("*.webp")], key=lambda f: natural_sort_key(f.name))
                items = []
                for idx, f in enumerate(webps, start=1):
                    with Image.open(f) as im:
                        w, h = im.size
                    rel = f.relative_to(OPT_DIR).as_posix()
                    items.append({
                        "order": idx,
                        "url": f"{BASE_URL}/{rel}",
                        "width": w,
                        "height": h,
                        "aspectRatio": calculate_aspect_ratio(w, h),
                        "sizeBytes": f.stat().st_size,
                        "format": "webp"
                    })
                catalog[brand_name]["carousel"]["Event-Carousel"] = items
        else:
            for proj in sorted([d for d in carousel_dir.iterdir() if d.is_dir()], key=lambda d: natural_sort_key(d.name)):
                webps = sorted([f for f in proj.glob("*.webp")], key=lambda f: natural_sort_key(f.name))
                items = []
                for idx, f in enumerate(webps, start=1):
                    with Image.open(f) as im:
                        w, h = im.size
                    rel = f.relative_to(OPT_DIR).as_posix()
                    items.append({
                        "order": idx,
                        "url": f"{BASE_URL}/{rel}",
                        "width": w,
                        "height": h,
                        "aspectRatio": calculate_aspect_ratio(w, h),
                        "sizeBytes": f.stat().st_size,
                        "format": "webp"
                    })
                catalog[brand_name]["carousel"][proj.name] = items
                
        # 2. Reel Covers
        for rc_name in ("Reel-Cover", "Reel-Covers"):
            rc_dir = b / rc_name
            if rc_dir.exists():
                webps = sorted([f for f in rc_dir.glob("*.webp")], key=lambda f: natural_sort_key(f.name))
                for idx, f in enumerate(webps, start=1):
                    with Image.open(f) as im:
                        w, h = im.size
                    rel = f.relative_to(OPT_DIR).as_posix()
                    catalog[brand_name]["reelCover"].append({
                        "order": idx,
                        "url": f"{BASE_URL}/{rel}",
                        "width": w,
                        "height": h,
                        "aspectRatio": calculate_aspect_ratio(w, h),
                        "sizeBytes": f.stat().st_size,
                        "format": "webp"
                    })
                    
        # 3. Posts & Posters
        for p_name in ("Post", "Event-Poster", "KBL-Signature-Packages-Collection-Posters"):
            p_dir = b / p_name
            if p_dir.exists():
                webps = sorted([f for f in p_dir.glob("*.webp")], key=lambda f: natural_sort_key(f.name))
                for idx, f in enumerate(webps, start=len(catalog[brand_name]["post"]) + 1):
                    with Image.open(f) as im:
                        w, h = im.size
                    rel = f.relative_to(OPT_DIR).as_posix()
                    catalog[brand_name]["post"].append({
                        "order": idx,
                        "url": f"{BASE_URL}/{rel}",
                        "width": w,
                        "height": h,
                        "aspectRatio": calculate_aspect_ratio(w, h),
                        "sizeBytes": f.stat().st_size,
                        "format": "webp"
                    })
                    
        # 4. Logo
        for l_name in ("Logo", "Keshvi-Beauty-Lounge-Logo"):
            l_dir = b / l_name
            if l_dir.exists():
                webps = sorted([f for f in l_dir.glob("*.webp")], key=lambda f: natural_sort_key(f.name))
                for idx, f in enumerate(webps, start=1):
                    with Image.open(f) as im:
                        w, h = im.size
                    rel = f.relative_to(OPT_DIR).as_posix()
                    catalog[brand_name]["logo"].append({
                        "order": idx,
                        "url": f"{BASE_URL}/{rel}",
                        "width": w,
                        "height": h,
                        "aspectRatio": calculate_aspect_ratio(w, h),
                        "sizeBytes": f.stat().st_size,
                        "format": "webp"
                    })
                    
        # 5. Highlights
        for h_name in ("Highlights", "Highlight-Covers"):
            h_dir = b / h_name
            if h_dir.exists():
                webps = sorted([f for f in h_dir.glob("*.webp")], key=lambda f: natural_sort_key(f.name))
                for idx, f in enumerate(webps, start=1):
                    with Image.open(f) as im:
                        w, h = im.size
                    rel = f.relative_to(OPT_DIR).as_posix()
                    catalog[brand_name]["highlights"].append({
                        "order": idx,
                        "url": f"{BASE_URL}/{rel}",
                        "width": w,
                        "height": h,
                        "aspectRatio": calculate_aspect_ratio(w, h),
                        "sizeBytes": f.stat().st_size,
                        "format": "webp"
                    })
                    
    return catalog

def generate_jsdelivr_markdown(catalog: dict, output_file: Path):
    lines = ["# jsDelivr Asset Links\n"]
    
    brand_display_names = {
        "Builders-Playground": "Builders Playground",
        "Cuts-and-Curves": "Cuts and Curves",
        "Keshvi-Beauty-Lounge": "Keshvi Beauty Lounge",
        "RanjeetRaj": "Ranjeet Raj",
        "WaterPlane": "WaterPlane"
    }
    
    for brand_key, brand_data in catalog.items():
        brand_title = brand_display_names.get(brand_key, brand_key.replace("-", " "))
        lines.append(f"## {brand_title}\n")
        
        # Carousel
        if brand_data["carousel"]:
            lines.append("### Carousel\n")
            for proj_key, items in brand_data["carousel"].items():
                proj_title = format_title_from_slug(proj_key)
                lines.append(f"#### {proj_title}\n")
                for item in items:
                    lines.append(f"{item['order']}.")
                    lines.append(f"{item['url']}\n")
                lines.append("")
                
        # Reel Cover
        if brand_data["reelCover"]:
            lines.append("### Reel Cover\n")
            for item in brand_data["reelCover"]:
                lines.append(f"{item['order']}.")
                lines.append(f"{item['url']}\n")
            lines.append("")
            
        # Post
        if brand_data["post"]:
            lines.append("### Post\n")
            for item in brand_data["post"]:
                lines.append(f"{item['order']}.")
                lines.append(f"{item['url']}\n")
            lines.append("")
            
        # Logo
        if brand_data["logo"]:
            lines.append("### Logo\n")
            for item in brand_data["logo"]:
                lines.append(f"{item['order']}.")
                lines.append(f"{item['url']}\n")
            lines.append("")
            
        # Highlights
        if brand_data["highlights"]:
            lines.append("### Highlights\n")
            for item in brand_data["highlights"]:
                lines.append(f"{item['order']}.")
                lines.append(f"{item['url']}\n")
            lines.append("")
            
        lines.append("---\n")
        
    output_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {output_file.name}")

def generate_json_output(catalog: dict, output_file: Path):
    output_file.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"Generated {output_file.name}")

def validate_pipeline(catalog: dict):
    print("\n" + "="*50)
    print("VALIDATION REPORT")
    print("="*50)
    
    total_brands = len(catalog)
    total_projects = 0
    total_webps = 0
    total_categories = set()
    errors = []
    
    for brand, data in catalog.items():
        for cat in ("carousel", "reelCover", "post", "logo", "highlights"):
            if data[cat]:
                total_categories.add(cat)
        
        # Check carousels
        for proj, items in data["carousel"].items():
            total_projects += 1
            total_webps += len(items)
            # Verify orders are 1..N
            orders = [it["order"] for it in items]
            if orders != list(range(1, len(items) + 1)):
                errors.append(f"Order mismatch in {brand}/Carousel/{proj}: {orders}")
            for it in items:
                # Check real file
                rel_path = it["url"].replace(f"{BASE_URL}/", "")
                real_file = OPT_DIR / rel_path
                if not real_file.exists():
                    errors.append(f"Missing file for URL: {it['url']}")
                if it["width"] <= 0 or it["height"] <= 0:
                    errors.append(f"Invalid dimensions for {real_file}")
                    
        for cat in ("reelCover", "post", "logo", "highlights"):
            items = data[cat]
            total_webps += len(items)
            orders = [it["order"] for it in items]
            if orders != list(range(1, len(items) + 1)):
                errors.append(f"Order mismatch in {brand}/{cat}: {orders}")
            for it in items:
                rel_path = it["url"].replace(f"{BASE_URL}/", "")
                real_file = OPT_DIR / rel_path
                if not real_file.exists():
                    errors.append(f"Missing file for URL: {it['url']}")
                    
    print(f"1. Total Brands Processed:     {total_brands}")
    print(f"2. Total Categories Processed: {len(total_categories)}")
    print(f"3. Total Carousel Projects:    {total_projects}")
    print(f"4. Total WebP Files:           {total_webps}")
    
    if errors:
        print(f"\n[ERROR] Found {len(errors)} validation errors:")
        for err in errors[:10]:
            print(f"  - {err}")
        return False
    else:
        print("\n[SUCCESS] All checks passed! 100% integrity verified.")
        return True

def main():
    docs_only = "--docs-only" in sys.argv or "-d" in sys.argv
    
    if not docs_only:
        # Remove old un-categorized RanjeetRaj folders if they exist
        old_rr_folders = [
            OPT_DIR / "RanjeetRaj" / "RR-01-Pro-Designer-Vocabulary-Carousel",
            OPT_DIR / "RanjeetRaj" / "RR-02-Attractive-Brand-Colors-Carousel",
            OPT_DIR / "RanjeetRaj" / "RR-03-The-Batching-System-Carousel",
            OPT_DIR / "RanjeetRaj" / "RR-04-Top-Canva-Background-Keywords-Carousel",
        ]
        for old_f in old_rr_folders:
            if old_f.exists():
                for child in old_f.iterdir():
                    child.unlink()
                old_f.rmdir()
                print(f"Cleaned up legacy folder: {old_f.name}")
                
        # Process brands
        process_ranjeet_raj()
        process_waterplane()
        process_cuts_and_curves()
    else:
        print("Running in --docs-only mode (skipping WebP conversion)...")
        
    # Build catalog & metadata
    catalog = build_asset_catalog()
    
    # Output docs
    generate_jsdelivr_markdown(catalog, REPO_ROOT / "jsdelivr-links.md")
    generate_json_output(catalog, REPO_ROOT / "design-assets.json")
    
    # Validate
    valid = validate_pipeline(catalog)
    if not valid:
        sys.exit(1)

if __name__ == "__main__":
    main()


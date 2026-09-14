import os
import shutil
from pathlib import Path

base_dir = Path("originals")
src_dir = base_dir / "Keshvi Beauty Lounge"
dest_dir = base_dir / "Keshvi-Beauty-Lounge"

if dest_dir.exists():
    shutil.rmtree(dest_dir)

def clean_name(name):
    name = name.replace("Carausal", "Carousel")
    name = name.replace("Beuty", "Beauty")
    name = name.replace(" ", "-")
    return name

if src_dir.exists():
    for root, dirs, files in os.walk(src_dir):
        rel_root = Path(root).relative_to(src_dir)
        clean_rel_parts = [clean_name(p) for p in rel_root.parts]
        dest_path = dest_dir.joinpath(*clean_rel_parts)
        dest_path.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            if file.lower().endswith(".png"):
                src_file = Path(root) / file
                dest_file = dest_path / clean_name(file)
                shutil.copy2(src_file, dest_file)
                
    shutil.rmtree(src_dir)
    print("Reorganization complete.")
else:
    print("Source directory not found.")

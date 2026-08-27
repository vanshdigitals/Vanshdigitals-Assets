"""
PNG -> WebP for Vansh Digitals assets.
Reads:  originals/**  (never modified)
Writes: optimized/**  (mirrors the same subfolders)
Run from the Design-Work-Gallery root:  python scripts/png-to-webp.py
"""
from PIL import Image
from pathlib import Path

SRC = Path("originals")
OUT = Path("optimized")
QUALITY = 88          # 85-90 looks identical; set LOSSLESS=True for zero loss
LOSSLESS = False
MAX_WIDTH = 2000      # downscale wider images; None = never resize
EXTS = {".png", ".jpg", ".jpeg", ".webp"}

def unique(path: Path) -> Path:
    if not path.exists(): return path
    i = 1
    while True:
        p = path.with_name(f"{path.stem}-{i}{path.suffix}")
        if not p.exists(): return p
        i += 1

def main():
    if not SRC.exists():
        print("No 'originals/' folder found. Run from the Design-Work-Gallery root."); return
    files = [p for p in SRC.rglob("*") if p.is_file() and p.suffix.lower() in EXTS]
    if not files:
        print("No images found under originals/."); return
    tb = ta = done = 0
    for p in files:
        try:
            img = Image.open(p)
            has_alpha = img.mode in ("RGBA","LA") or (img.mode=="P" and "transparency" in img.info)
            img = img.convert("RGBA") if has_alpha else img.convert("RGB")
            if MAX_WIDTH and img.width > MAX_WIDTH:
                h = round(img.height * MAX_WIDTH / img.width)
                img = img.resize((MAX_WIDTH, h), Image.LANCZOS)
            rel = p.relative_to(SRC).with_suffix(".webp")
            out = unique(OUT / rel)
            out.parent.mkdir(parents=True, exist_ok=True)
            kw = {"format":"WEBP","method":6}
            kw["lossless"] = True if LOSSLESS else kw.__setitem__("quality", QUALITY)
            if LOSSLESS: kw = {"format":"WEBP","method":6,"lossless":True}
            else: kw = {"format":"WEBP","method":6,"quality":QUALITY}
            img.save(out, **kw)
            b, a = p.stat().st_size, out.stat().st_size
            tb += b; ta += a; done += 1
            print(f"OK  {rel}  {b//1024}KB -> {a//1024}KB (-{100*(1-a/b):.0f}%)")
        except Exception as e:
            print(f"SKIP {p}: {e}")
    if done:
        print(f"\nConverted {done} files. {tb//1024//1024}MB -> {ta//1024//1024}MB (-{100*(1-ta/tb):.0f}%)")
        print("Originals untouched. Now push the 'optimized/' folder to GitHub.")

if __name__ == "__main__":
    main()

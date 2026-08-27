# Vansh Digitals - Design Assets

This repository holds the optimized WebP images for the Vansh Digitals portfolio website.

## Local Workflow
1. Add new PNG/JPG originals to `originals/<brand>/`. These are **never** committed.
2. Run `python scripts/png-to-webp.py` from the root directory.
3. The optimized WebP images will be placed in `optimized/<brand>/`.
4. Commit and push the `optimized/` folder to GitHub.

## Usage in Website
The images are served via jsDelivr CDN.

**URL format:**
```
https://cdn.jsdelivr.net/gh/vanshdigitals/Vanshdigitals-Assets@main/optimized/<brand>/<file>.webp
```

**Example:**
```
https://cdn.jsdelivr.net/gh/vanshdigitals/Vanshdigitals-Assets@main/optimized/cuts-curves/carousel-01.webp
```

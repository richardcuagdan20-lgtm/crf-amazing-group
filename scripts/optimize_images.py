#!/usr/bin/env python3
"""Resize official project photos to web sizes as WebP. Originals stay in assets/projects/."""
import json
import sys
from pathlib import Path
from PIL import Image

SRC = Path("/workspace/mamcris-site/assets/projects")
DST = Path("/workspace/mamcris-site/site/public/images/projects")
DATA = Path("/workspace/mamcris-site/site/src/data")
MAX = {"hero": 1600, "gallery_or_amenity": 1400, "plan": 1800, "amenity": 1400}
QUALITY = {"hero": 80, "gallery_or_amenity": 78, "plan": 82, "amenity": 78}

def webp_name(rel: str) -> str:
    p = Path(rel)
    return str(p.with_suffix(".webp"))

def optimize(src: Path, dest: Path, max_w: int, quality: int) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src)
    im = im.convert("RGB") if im.mode in ("RGBA", "P", "LA") else im.convert("RGB")
    w, h = im.size
    if w > max_w:
        nh = int(h * max_w / w)
        im = im.resize((max_w, nh), Image.Resampling.LANCZOS)
        w, h = im.size
    im.save(dest, "WEBP", quality=quality, method=6)
    return {"width": w, "height": h, "bytes": dest.stat().st_size}

def main():
    catalog = json.loads((SRC / "projects.json").read_text())
    out_projects = []
    errors = []
    for proj in catalog["projects"]:
        images = []
        for im in proj["images"]:
            role = im.get("role") or "gallery_or_amenity"
            src = SRC / im["file"]
            rel_webp = webp_name(im["file"])
            dest = DST / rel_webp
            try:
                info = optimize(src, dest, MAX.get(role, 1400), QUALITY.get(role, 78))
                images.append({
                    "file": rel_webp,
                    "role": "gallery_or_amenity" if role == "amenity" else role,
                    "width": info["width"],
                    "height": info["height"],
                    "bytes": info["bytes"],
                    "alt": f"{proj['name']} — {role.replace('_', ' ')}",
                })
                print(f"ok {rel_webp} {info['bytes']}")
            except Exception as e:
                errors.append({"file": im["file"], "error": str(e)})
                print(f"FAIL {im['file']}: {e}", file=sys.stderr)
        status = proj.get("status") or ""
        is_rfo = "ready for occupancy" in status.lower()
        is_presell = "pre-sell" in status.lower()
        hero = next((i for i in images if i["role"] == "hero"), images[0] if images else None)
        out_projects.append({
            "name": proj["name"],
            "slug": proj["slug"],
            "location": proj.get("location") or "",
            "city": proj.get("city") or "",
            "type": proj.get("type") or "condo",
            "status": status or None,
            "is_rfo": is_rfo,
            "is_preselling": is_presell,
            "facts": proj.get("facts") or {},
            "source_url": proj.get("source_url"),
            "hero": hero,
            "gallery": [i for i in images if i["role"] == "gallery_or_amenity"],
            "plans": [i for i in images if i["role"] == "plan"],
            "images": images,
        })
    DATA.mkdir(parents=True, exist_ok=True)
    payload = {
        "projects": out_projects,
        "errors": errors,
        "source": "Official rlcresidences.com photos, optimized for the web. Originals remain in /workspace/mamcris-site/assets/projects/.",
    }
    (DATA / "projects.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote data for {len(out_projects)} projects, {sum(len(p['images']) for p in out_projects)} web images, {len(errors)} errors")

if __name__ == "__main__":
    main()

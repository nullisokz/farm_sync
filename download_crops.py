# download_crops.py
# Gets images of crops from Bing and saves them as .jpg in images_flat/
# Needs: pip install bing-image-downloader pillow

import os
import shutil
from pathlib import Path
from PIL import Image

# 1) your crops here (should match what the model predicts)
items = [
    "rice",
    "maize",
    "chickpea",
    "kidneybeans",
    "pigeonpeas",
    "mothbeans",
    "mungbean",
    "blackgram",
    "lentil",
    "pomegranate",
    "banana",
    "mango",
    "grapes",
    "watermelon",
    "muskmelon",
    "apple",
    "orange",
    "papaya",
    "coconut",
    "cotton",
    "jute",
    "coffee",
]

# 2) Better search phrases (to get the right type of image)
query_map = {
    "rice": "rice plant field",
    "maize": "maize corn plant field",
    "chickpea": "chickpea plant",
    "kidneybeans": "kidney beans plant",
    "pigeonpeas": "pigeon peas plant",
    "mothbeans": "moth beans plant",
    "mungbean": "mung bean plant",
    "blackgram": "black gram urad dal plant",
    "lentil": "lentil plant",
    "pomegranate": "pomegranate fruit on tree",
    "banana": "banana fruit",
    "mango": "mango fruit",
    "grapes": "grapes fruit bunch",
    "watermelon": "watermelon fruit whole",
    "muskmelon": "muskmelon cantaloupe fruit",
    "apple": "apple fruit",
    "orange": "orange fruit",
    "papaya": "papaya fruit",
    "coconut": "coconut fruit",
    "cotton": "cotton plant boll",
    "jute": "jute plant",
    "coffee": "coffee plant coffee cherries",
}

# 3) Import and possibly auto-install
try:
    from bing_image_downloader import downloader
except ImportError:
    raise SystemExit(
        "Package 'bing-image-downloader' is missing.\n"
        "Install with:  pip install bing-image-downloader pillow"
    )

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "images"         # here the package creates subfolders per search term
FLAT_DIR = BASE_DIR / "images_flat"   # finished .jpg with correct names
RAW_DIR.mkdir(exist_ok=True)
FLAT_DIR.mkdir(exist_ok=True)

def download_one(query: str, limit: int = 1):
    """
    Gets 'limit' images for given search term into a subfolder under RAW_DIR.
    """
    downloader.download(
        query=query,
        limit=limit,
        output_dir=str(RAW_DIR),
        adult_filter_off=True,
        force_replace=False,
        timeout=60,
        verbose=True,
    )

def first_file_in(folder: Path):
    if not folder.exists():
        return None
    for p in folder.iterdir():
        if p.is_file():
            return p
        # the package often puts images in an additional level (e.g. 'Image_1.jpg')
        if p.is_dir():
            for f in p.iterdir():
                if f.is_file():
                    return f
    return None

def to_jpg(src_path: Path, dst_path: Path):
    """
    Converts (or copies) to .jpg with PIL for stable format and
    changes color mode if necessary.
    """
    try:
        with Image.open(src_path) as im:
            if im.mode in ("RGBA", "P"):
                im = im.convert("RGB")
            im.save(dst_path, format="JPEG", quality=90, optimize=True)
    except Exception:
        # If PIL cannot open the file, make a clean copy (might already be .jpg)
        shutil.copy2(src_path, dst_path)

def main():
    for item in items:
        query = query_map.get(item, item)
        print(f"\n=== Hämtar: {item} | sökfråga: '{query}' ===")
        # 1) Download
        download_one(query, limit=1)

        # 2) Find the first downloaded file
        # bing_image_downloader creates a folder with the exact query name
        query_folder = RAW_DIR / query
        src = first_file_in(query_folder)
        if not src:
            # fallback: sometimes item is used as folder name
            src = first_file_in(RAW_DIR / item)

        if not src:
            print(f"❗ Could not find downloaded image for: {item}")
            continue

        # 3) Save as <item>.jpg in images_flat/
        dst = FLAT_DIR / f"{item}.jpg"
        to_jpg(src, dst)
        print(f"✅ Saved: {dst}")

    print("\nDone! All images (as many as could be fetched) are in:", FLAT_DIR)

if __name__ == "__main__":
    main()

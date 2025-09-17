# download_crops.py
# Hämtar 1 bild per gröda och sparar som <namn>.jpg i images_flat/
# Kräver: pip install bing-image-downloader pillow

import os
import shutil
from pathlib import Path
from PIL import Image

# 1) Ditt urval
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

# 2) Bättre sökfraser (så vi får rätt typ av bild)
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

# 3) Import och ev. auto-install
try:
    from bing_image_downloader import downloader
except ImportError:
    raise SystemExit(
        "Package 'bing-image-downloader' saknas.\n"
        "Installera med:  pip install bing-image-downloader pillow"
    )

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "images"         # här skapar paketet undermappar per sökord
FLAT_DIR = BASE_DIR / "images_flat"   # färdiga .jpg med rätt namn
RAW_DIR.mkdir(exist_ok=True)
FLAT_DIR.mkdir(exist_ok=True)

def download_one(query: str, limit: int = 1):
    """
    Hämtar 'limit' bilder för given sökfråga in i en undermapp under RAW_DIR.
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
        # paketet lägger ofta bilder i ytterligare en nivå (t.ex. 'Image_1.jpg')
        if p.is_dir():
            for f in p.iterdir():
                if f.is_file():
                    return f
    return None

def to_jpg(src_path: Path, dst_path: Path):
    """
    Konverterar (eller kopierar) till .jpg med PIL för stabilt format och
    byter färgläge om nödvändigt.
    """
    try:
        with Image.open(src_path) as im:
            if im.mode in ("RGBA", "P"):
                im = im.convert("RGB")
            im.save(dst_path, format="JPEG", quality=90, optimize=True)
    except Exception:
        # Om PIL inte kan öppna filen, gör en ren kopia (kan vara redan .jpg)
        shutil.copy2(src_path, dst_path)

def main():
    for item in items:
        query = query_map.get(item, item)
        print(f"\n=== Hämtar: {item} | sökfråga: '{query}' ===")
        # 1) Ladda ner
        download_one(query, limit=1)

        # 2) Hitta första filen som laddats ned
        # bing_image_downloader skapar mapp med exakt query-namnet
        query_folder = RAW_DIR / query
        src = first_file_in(query_folder)
        if not src:
            # fallback: ibland används item som mappnamn
            src = first_file_in(RAW_DIR / item)

        if not src:
            print(f"❗ Kunde inte hitta nerladdad bild för: {item}")
            continue

        # 3) Spara som <item>.jpg i images_flat/
        dst = FLAT_DIR / f"{item}.jpg"
        to_jpg(src, dst)
        print(f"✅ Sparad: {dst}")

    print("\nKlart! Alla bilder (så många som gick att hämta) finns i:", FLAT_DIR)

if __name__ == "__main__":
    main()

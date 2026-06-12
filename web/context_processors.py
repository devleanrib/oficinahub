from pathlib import Path
import os

ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
LOGO_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp"]


def shop_context(request):
    from web.models import ShopSettings

    shop = ShopSettings.objects.first()
    if not shop:
        shop = ShopSettings.objects.create()

    logo_path = None
    for ext in LOGO_EXTENSIONS:
        path = ASSETS_DIR / f"logo{ext}"
        if path.is_file():
            resolved = str(path.resolve())
            if os.name == "nt":
                logo_path = "file:///" + resolved.replace("\\", "/")
            else:
                logo_path = "file://" + resolved
            break

    return {
        "shop": shop,
        "shop_logo_path": logo_path,
    }

import os
import shutil
import json

HOME_DIR = os.path.expanduser("~")
VORTEX_PATH = f"{HOME_DIR}/vortex"
VORTEX_ASSETS = f"{HOME_DIR}/vortex/assets"
VORTEX_SETTINGS = f"{HOME_DIR}/vortex/settings.json"

BACKGROUND_IMAGE = None
THEME_COLOR = None


def load_settings() -> dict:
    global BACKGROUND_IMAGE, THEME_COLOR
    with open(VORTEX_SETTINGS, "r") as f:
        d = json.load(f)

    BACKGROUND_IMAGE = d["bg_image"]
    THEME_COLOR = d["theme_color"]

    return d


def set_settings(bg_image=None, theme_color: list = None) -> bool:
    with open(VORTEX_SETTINGS, "r") as fr:
        d = json.load(fr)
        if bg_image:
            d["bg_image"] = bg_image
        if theme_color:
            d["theme_color"] = theme_color

    with open(VORTEX_SETTINGS, "w") as fw:
        json.dump(d, fw, indent=4)

    fw.close()

    return True


def setup_vortex() -> None:
    if not os.path.exists(VORTEX_PATH):
        os.mkdir(VORTEX_PATH)

    if not os.path.exists(VORTEX_ASSETS):
        os.mkdir(VORTEX_ASSETS)
        shutil.copy("images/background.jpg", f"{VORTEX_ASSETS}/background.jpg")

    if not os.path.exists(VORTEX_SETTINGS):
        settings_data = {
            "bg_image": f"{VORTEX_ASSETS}/background.jpg",
            "theme_color": [7, 23, 26],
        }
        with open(VORTEX_SETTINGS, "w") as f:
            json.dump(settings_data, f, indent=4)

        f.close()

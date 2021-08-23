import pathlib

MODULE_ROOT = pathlib.Path(__file__).resolve().parent


with open(MODULE_ROOT / "VERSION") as f:
    __version__ = f.read().strip()

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

# Import constants and helpers from utils.py (assumed to be ported)
from utils import lib_path, TAG, OWNER, REPO, dirname

PLATFORM_NAME = platform.system().lower()
ARG = sys.argv[1] if len(sys.argv) > 1 else None
TARGET = sys.argv[2] if len(sys.argv) > 2 else None

TARGET_TRIPLE = None
if TARGET and TARGET.startswith("--target="):
    TARGET_TRIPLE = TARGET.replace("--target=", "")

LIB = [
    "skia",
    "skparagraph",
    "skshaper",
    "svg",
    "skunicode_core",
    "skunicode_icu",
    "skottie",
    "skresources",
    "sksg",
    "jsonreader",
]
ICU_DAT = "icudtl.dat"


def download():
    os.makedirs(
        os.path.dirname(lib_path("skia", PLATFORM_NAME, TARGET_TRIPLE)["binary"]),
        exist_ok=True,
    )
    for lib in LIB:
        paths = lib_path(lib, PLATFORM_NAME, TARGET_TRIPLE)
        download_url = paths["downloadUrl"]
        binary = paths["binary"]
        print(f"downloading {download_url} to {binary}")
        subprocess.run(
            [
                "curl",
                "-J",
                "-L",
                "-H",
                "Accept: application/octet-stream",
                download_url,
                "-o",
                binary,
            ],
            check=True,
        )
    if PLATFORM_NAME == "windows":
        download_icu()


def download_icu():
    download_url = (
        f"https://github.com/{OWNER}/{REPO}/releases/download/{TAG}/{ICU_DAT}"
    )
    subprocess.run(
        [
            "curl",
            "-J",
            "-L",
            "-H",
            "Accept: application/octet-stream",
            download_url,
            "-o",
            ICU_DAT,
        ],
        check=True,
    )
    shutil.move(
        os.path.join(dirname, "..", ICU_DAT),
        os.path.join(dirname, "..", "canvas_pyr", ICU_DAT),
    )


def main():
    if ARG == "--download":
        download()
    elif ARG == "--download-icu":
        download_icu()
    else:
        raise TypeError(f"Unknown arguments [{ARG}]")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(1)

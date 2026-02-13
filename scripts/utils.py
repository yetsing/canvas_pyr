from __future__ import annotations

import os
import subprocess
from pathlib import Path

OWNER = "Brooooooklyn"
REPO = "canvas"


def _get_full_hash() -> str:
    if os.getenv("NODE_ENV") == "ava":
        full_hash = "000000"
    else:
        output = subprocess.check_output(
            ["git", "submodule", "status", "skia"], text=True
        ).strip()
        full_hash = output.split(" ")[0]
    if not full_hash[0].isalnum():
        full_hash = full_hash[1:]
    return full_hash


FULL_HASH = _get_full_hash()
SHORT_HASH = FULL_HASH[:8]

dirname = str(Path(__file__).resolve().parent)

TAG = f"skia-{SHORT_HASH}"


def lib_path(
    lib: str, host_platform: str, triple: str | None, tag: str = TAG
) -> dict[str, str]:
    platform_name: str
    if not triple:
        if host_platform == "windows":
            platform_name = f"{lib}-win32-x64-msvc.lib"
        elif host_platform == "darwin":
            platform_name = f"lib{lib}-darwin-x64.a"
        elif host_platform == "linux":
            platform_name = f"lib{lib}-linux-x64-gnu.a"
        else:
            raise TypeError(f"[{host_platform}] is not a valid platform")
    else:
        if triple == "aarch64-unknown-linux-gnu":
            platform_name = f"lib{lib}-linux-aarch64-gnu.a"
        elif triple == "aarch64-unknown-linux-musl":
            platform_name = f"lib{lib}-linux-aarch64-musl.a"
        elif triple == "armv7-unknown-linux-gnueabihf":
            platform_name = f"lib{lib}-linux-armv7-gnueabihf.a"
        elif triple == "x86_64-unknown-linux-musl":
            platform_name = f"lib{lib}-linux-x64-musl.a"
        elif triple == "aarch64-apple-darwin":
            platform_name = f"lib{lib}-darwin-aarch64.a"
        elif triple == "aarch64-linux-android":
            platform_name = f"lib{lib}-android-aarch64.a"
        elif triple == "riscv64gc-unknown-linux-gnu":
            platform_name = f"lib{lib}-linux-riscv64-gnu.a"
        elif triple == "aarch64-pc-windows-msvc":
            platform_name = f"{lib}-win32-arm64-msvc.lib"
        else:
            raise TypeError(f"[{triple}] is not a valid target")

    binary = str(
        Path(dirname).parent
        / "skia"
        / "out"
        / "Static"
        / (f"{lib}.lib" if host_platform == "win32" else f"lib{lib}.a")
    )
    copy = str(Path(dirname).parent / platform_name)
    download_url = (
        f"https://github.com/{OWNER}/{REPO}/releases/download/{tag}/{platform_name}"
    )
    return {
        "binary": binary,
        "copy": copy,
        "downloadUrl": download_url,
        "filename": platform_name,
    }

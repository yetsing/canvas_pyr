import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path
from unittest import skip
from zipfile import ZipFile, ZipInfo

try:
    import tomllib as _toml_read  # Python 3.11+
except ModuleNotFoundError:
    import tomli as _toml_read  # pip install tomli

script_dir = Path(__file__).resolve().parent
upstream_dir = script_dir / "canvas_upstream"


def load_toml_path(path):
    with open(path, "rb") as f:
        return _toml_read.load(f)


def get_upstream_version():
    data = load_toml_path(str(script_dir.parent / "pyproject.toml"))
    return data["tool"]["canvas_pyr"]["upstream"]["version"]


def skip_if_sign(version: str) -> bool:
    sign_path = upstream_dir / "version_sign.txt"
    return (
        sign_path.exists()
        and sign_path.is_file()
        and sign_path.read_text().strip() == version
    )


def make_sign(version: str):
    sign_path = upstream_dir / "version_sign.txt"
    sign_path.parent.mkdir(parents=True, exist_ok=True)
    sign_path.write_text(version)


def safe_extract(zip_path: str | Path, dest_dir: str | Path) -> None:
    dest_dir = Path(dest_dir).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    with ZipFile(zip_path, "r") as z:
        names = [
            m.filename
            for m in z.infolist()
            if m.filename and not m.filename.endswith("/")
        ]
        top_parts = [Path(n).parts[0] for n in names if Path(n).parts]
        drop_top = len(set(top_parts)) == 1
        top_dir = top_parts[0] if drop_top and top_parts else None

        for member in z.infolist():
            # Normalize the target path and ensure it's inside dest_dir
            member_path = Path(member.filename)
            if top_dir and member_path.parts and member_path.parts[0] == top_dir:
                member_path = Path(*member_path.parts[1:])

            if not member_path.parts:
                continue

            target_path = dest_dir.joinpath(member_path)
            resolved = target_path.resolve()
            if not str(resolved).startswith(str(dest_dir)):
                raise RuntimeError(
                    f"Unsafe path detected in zip file: {member.filename}"
                )

            # Create directories as needed
            if member.is_dir():
                resolved.mkdir(parents=True, exist_ok=True)
                continue

            resolved.parent.mkdir(parents=True, exist_ok=True)
            # Extract file content safely
            with z.open(member, "r") as src, open(resolved, "wb") as dst:
                shutil.copyfileobj(src, dst)

            # Preserve unix permissions if present
            perm = member.external_attr >> 16
            if perm:
                try:
                    resolved.chmod(perm)
                except Exception:
                    # 某些平台（如 Windows）可能忽略 chmod
                    pass


def download_upstream_resource(version: str):
    url = f"https://github.com/Brooooooklyn/canvas/archive/refs/tags/v{version}.zip"
    filename = f"canvas-{version}.zip"
    with tempfile.TemporaryDirectory() as td:
        zip_path = script_dir / filename
        if not zip_path.exists():
            zip_path = Path(td) / f"canvas-{version}.zip"
            urllib.request.urlretrieve(url, zip_path)
        safe_extract(zip_path, upstream_dir)

    url = "https://github.com/samuelngs/apple-emoji-linux/releases/download/v18.4/AppleColorEmoji.ttf"
    font_path = upstream_dir.joinpath("__test__", "fonts", "AppleColorEmoji.ttf")
    font_path.parent.mkdir(parents=True, exist_ok=True)
    if not font_path.exists():
        urllib.request.urlretrieve(url, font_path)


def main():
    version = get_upstream_version()
    if skip_if_sign(version):
        print(f"Upstream version {version} already downloaded, skip.")
        return
    shutil.rmtree(script_dir / "__test__", ignore_errors=True)
    download_upstream_resource(version)
    make_sign(version)


if __name__ == "__main__":
    main()

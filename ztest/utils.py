import pathlib
import platform
import unittest
from io import BytesIO
from typing import Literal, Optional

import canvas_pyr


from PIL import Image

DEFAULT_WIDTH = 350
DEFAULT_HEIGHT = 150

script_dir = pathlib.Path(__file__).resolve().parent
upstream_dir = script_dir / "canvas_upstream"


def multi_startswith(s: str, prefixes: list[str]) -> bool:
    """Check if string `s` starts with any of the given `prefixes`."""
    return any(s.startswith(prefix) for prefix in prefixes)


class BaseTestCase(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.canvas = canvas_pyr.createCanvas(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.ctx = self.canvas.getContext("2d")

    def _load_ava_snapshot(self, filename: str) -> None:

        def _s(line: str) -> str:
            return line[4:]  # remove leading "    " from data lines in snapshot files

        def _h(s: str) -> str:
            return s.replace("␊", "\n")  # unescape newlines in snapshot data

        snap_path = self._test_path(filename)
        lines = snap_path.read_text().splitlines()

        mapping = {}
        name = ""
        quote_closed = True
        quote = ""
        for line in lines:
            if not quote_closed:
                line = _s(line)
                mapping[name] += line
                if line.endswith(quote):
                    mapping[name] = mapping[name][:-1]
                    quote_closed = True
                    name = ""
                continue
            if line.startswith("## "):
                name = line[3:]
            elif name and multi_startswith(_s(line), ["'", "`"]):
                line = _s(line)
                quote = line[0]
                if line.endswith(quote):
                    mapping[name] = line[1:-1]
                    name = ""
                else:
                    mapping[name] = line[1:]
                    quote_closed = False

        for k in list(mapping.keys()):
            mapping[k] = _h(mapping[k])
        self._snapshot_mapping = mapping

    def _ava_snapshot(self, title: str, got: str):
        self.assertIn(title, self._snapshot_mapping)
        self.assertEqual(got, self._snapshot_mapping[title])

    def _snapshot(
        self,
        title: str,
        type_: Literal["png", "jpeg", "webp", "avif"] = "png",
        different_ratio: Optional[float] = None,
        canvas: Optional[canvas_pyr.Canvas] = None,
    ):
        canvas = canvas or self.canvas
        snapshot_image(self, title, canvas, type_, different_ratio)

    def _test_path(self, *args: str) -> pathlib.Path:
        return upstream_dir / "__test__" / pathlib.Path(*args)

    def _example_path(self, *args: str) -> pathlib.Path:
        return upstream_dir / "example" / pathlib.Path(*args)

    def _load_image(self, filename: str) -> canvas_pyr.Image:
        image = canvas_pyr.Image()
        image_path = self._test_path(filename)
        image.load(image_path.read_bytes())
        return image

    def _load_image1(self, filename: str) -> canvas_pyr.Image:
        image = canvas_pyr.Image()
        image_path = self._test_path(filename)
        image.load(str(image_path))
        return image

    def _load_image2(self, *args: str) -> canvas_pyr.Image:
        image = canvas_pyr.Image()
        image_path = self._test_path(*args)
        image.load(image_path.read_bytes())
        return image


def snapshot_image(
    t: unittest.TestCase,
    title: str,
    canvas,
    type_: Literal["png", "jpeg", "webp", "avif"] = "png",
    different_ratio: Optional[float] = None,
) -> None:

    if different_ratio is None:
        is_x64 = platform.machine().lower() in {"x86_64", "amd64"}
        different_ratio = 0.015 if is_x64 else (2.5 if "filter" in title else 0.3)

    image = canvas.encode(type_, 100)
    ext = "jpg" if type_ == "jpeg" else type_
    base_dir = upstream_dir / "__test__"
    snap_path = base_dir / "snapshots" / f"{title}.{ext}"
    fail_path = base_dir / "failure" / f"{title}.{ext}"

    def write_failure_image() -> None:
        fail_path.parent.mkdir(parents=True, exist_ok=True)
        fail_path.write_bytes(image)

    # if not snap_path.exists() or os.getenv("UPDATE_SNAPSHOT"):
    #     snap_path.parent.mkdir(parents=True, exist_ok=True)
    #     snap_path.write_bytes(image)
    #     return

    existed = snap_path.read_bytes()
    if type_ not in {"png", "jpeg"}:
        return

    existed_pixels = Image.open(BytesIO(existed)).tobytes()
    image_pixels = Image.open(BytesIO(image)).tobytes()

    if len(existed_pixels) != len(image_pixels):
        write_failure_image()
        return t.fail("Image size is not equal")

    diff_count = sum(1 for i, b in enumerate(image_pixels) if b != existed_pixels[i])
    if diff_count / len(existed_pixels) > different_ratio / 100:
        write_failure_image()
        ratio = (diff_count / len(existed_pixels)) * 100
        return t.fail(f"Image bytes is not equal, different ratio is {ratio:.2f}%")

    return

import pathlib
import sys
import unittest
from pathlib import Path
from typing import Literal, Optional

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import snapshot_image, upstream_dir

FIREFOX = (upstream_dir / "__test__" / "fixtures" / "firefox-logo.svg").read_bytes()
FIREFOX_IMAGE = canvas_pyr.Image(200, 206.433)
FIREFOX_IMAGE.load(FIREFOX)


class FilterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.canvas = canvas_pyr.createCanvas(300, 300)
        self.ctx = self.canvas.getContext("2d")

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

    def _load_image(self, filename: str) -> canvas_pyr.Image:
        image = canvas_pyr.Image()
        image_path = self._test_path("fixtures", filename)
        image.load(image_path.read_bytes())
        return image

    def test_filter_blur(self):
        ctx = self.ctx
        ctx.filter = "blur(5px)"
        ctx.drawImage(FIREFOX_IMAGE, 0, 0)
        self._snapshot("filter-blur")

    def test_filter_brightness(self):
        ctx = self.ctx
        ctx.filter = "brightness(2)"
        image = canvas_pyr.Image()
        data = self._test_path("fixtures", "filter-brightness.jpg").read_bytes()
        image.load(data)
        ctx.drawImage(image, 0, 0)
        self._snapshot("filter-brightness")

    def test_filter_contrast(self):
        ctx = self.ctx
        ctx.filter = "contrast(200%)"
        image = canvas_pyr.Image()
        data = self._test_path("fixtures", "filter-contrast.jpeg").read_bytes()
        image.load(data)
        ctx.drawImage(image, 0, 0)
        self._snapshot("filter-contrast")

    def test_filter_ccontrast_ff(self):
        ctx = self.ctx
        ctx.filter = "contrast(200%)"
        ctx.drawImage(FIREFOX_IMAGE, 0, 0)
        self._snapshot("filter-contrast-ff")

    def test_filter_grayscale(self):
        ctx = self.ctx
        ctx.filter = "grayscale(80%)"
        ctx.drawImage(FIREFOX_IMAGE, 0, 0)
        self._snapshot("filter-grayscale")

    def test_hue_rotate(self):
        ctx = self.ctx
        ctx.filter = "hue-rotate(90deg)"
        ctx.drawImage(FIREFOX_IMAGE, 0, 0)
        self._snapshot("filter-hue-rotate")

    def test_drop_shadow(self):
        ctx = self.ctx
        ctx.filter = "drop-shadow(16px 16px 10px black)"
        ctx.drawImage(self._load_image("filter-drop-shadow.jpeg"), 0, 0)
        self._snapshot("filter-drop-shadow")

    def test_filter_invert(self):
        ctx = self.ctx
        ctx.filter = "invert(100%)"
        ctx.drawImage(self._load_image("filter-invert.jpeg"), 0, 0)
        self._snapshot("filter-invert")

    def test_filter_opacity(self):
        ctx = self.ctx
        ctx.filter = "opacity(20%)"
        ctx.drawImage(self._load_image("filter-opacity.jpeg"), 0, 0)
        self._snapshot("filter-opacity")

    def test_filter_saturate(self):
        ctx = self.ctx
        ctx.filter = "saturate(200%)"
        ctx.drawImage(self._load_image("filter-saturate.jpeg"), 0, 0)
        self._snapshot("filter-saturate")

    def test_filter_sepia(self):
        ctx = self.ctx
        ctx.filter = "sepia(100%)"
        ctx.drawImage(self._load_image("filter-sepia.jpeg"), 0, 0)
        self._snapshot("filter-sepia", "png", 0.05)

    def test_filter_combine_contrast_brightness(self):
        ctx = self.ctx
        ctx.filter = "contrast(175%) brightness(103%)"
        ctx.drawImage(self._load_image("filter-combine-contrast-brightness.jpeg"), 0, 0)
        self._snapshot("filter-combine-contrast-brightness")

    def test_filter_save_restore(self):
        ctx = self.ctx
        ctx.filter = "none"
        ctx.save()
        ctx.filter = "invert(100%)"
        ctx.restore()
        ctx.drawImage(self._load_image("filter-invert.jpeg"), 0, 0)
        self._snapshot("filter-save-restore")

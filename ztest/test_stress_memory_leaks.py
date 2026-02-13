import base64
import math
import os
import pathlib
import platform
import sys
import tempfile
import time
import unittest
from pathlib import Path

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import BaseTestCase


class StressMemoryLeaksTestCase(BaseTestCase):
    ITERATIONS = 500

    def test_canvas_pattern(self):
        canvas = canvas_pyr.createCanvas(256, 256)
        ctx = canvas.getContext("2d")
        pattern_canvas = canvas_pyr.createCanvas(32, 32)
        pattern_ctx = pattern_canvas.getContext("2d")

        for i in range(self.ITERATIONS):
            pattern_ctx.fillStyle = f"rgb({i % 256}, {(i * 7) % 256}, {(i * 13) % 256})"
            pattern_ctx.fillRect(0, 0, 32, 32)

            pattern = ctx.createPattern(pattern_canvas, "repeat")
            ctx.fillStyle = pattern
            ctx.fillRect(0, 0, 256, 256)

    def test_svg_image_decode(self):
        svg_text = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
            + '<rect width="100" height="100" fill="red"/>'
            + '<circle cx="50" cy="50" r="40" fill="blue"/>'
            + "</svg>"
        )

        for i in range(self.ITERATIONS):
            image = canvas_pyr.Image()
            image.load(svg_text.encode("utf-8"))
            # Draw it to exercise the full pipeline
            canvas = canvas_pyr.createCanvas(100, 100)
            ctx = canvas.getContext("2d")
            ctx.drawImage(image, 0, 0)

    def test_convert_svg_text_to_path(self):
        font_path = self._test_path("fonts", "iosevka-slab-regular.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path))
        svg_fixture = self._test_path("text.svg").read_text(encoding="utf-8")

        for i in range(self.ITERATIONS):
            result = canvas_pyr.convertSVGTextToPath(svg_fixture)
            self.assertGreater(len(result), 0)

    def test_svg_canvas_get_content(self):
        for i in range(self.ITERATIONS):
            canvas = canvas_pyr.createCanvas(
                200, 200, canvas_pyr.SvgExportFlag.ConvertTextToPaths
            )
            ctx = canvas.getContext("2d")
            ctx.fillStyle = "red"
            ctx.fillRect(0, 0, 200, 200)

            # getContent destroys the canvas, creates a new one, then object is dropped
            # This tests the null-out-after-destroy + Drop interaction
            content = canvas.getContent()
            self.assertGreater(len(content), 0)

    def test_svg_canvas_resize(self):
        for i in range(self.ITERATIONS):
            canvas = canvas_pyr.createCanvas(
                200, 200, canvas_pyr.SvgExportFlag.ConvertTextToPaths
            )
            ctx = canvas.getContext("2d")
            ctx.fillStyle = "red"
            ctx.fillRect(0, 0, 200, 200)

            # Resize triggers mem::replace which drops old Context
            # The old SVG canvas must be destroyed in Drop without double-free
            canvas.width = 100 + (i % 100)
            canvas.height = 100 + (i % 100)

            ctx.fillRect(0, 0, canvas.width, canvas.height)
            content = canvas.getContent()
            self.assertGreater(len(content), 0)

    def test_svg_canvas_without_get_content(self):
        for i in range(self.ITERATIONS):
            canvas = canvas_pyr.createCanvas(
                128, 128, canvas_pyr.SvgExportFlag.ConvertTextToPaths
            )
            ctx = canvas.getContext("2d")
            ctx.fillStyle = f"hsl({i % 360}, 80%, 50%)"
            ctx.fillRect(0, 0, 128, 128)
            # Just drop the canvas without calling getContent to ensure Drop works correctly

    def test_svg_canvas_with_various_sizes(self):
        for i in range(self.ITERATIONS):
            w = 1 + (i % 500)
            h = 1 + ((i * 7) % 500)
            canvas = canvas_pyr.createCanvas(
                w, h, canvas_pyr.SvgExportFlag.ConvertTextToPaths
            )
            ctx = canvas.getContext("2d")
            ctx.fillRect(0, 0, w, h)
            content = canvas.getContent()
            self.assertGreater(len(content), 0)

    def test_path2d_from_svg_string(self):
        paths = [
            "M 10 80 C 40 10, 65 10, 95 80 S 150 150, 180 80",
            "M 0 0 L 100 0 L 100 100 L 0 100 Z",
            "M108.956,403.826c0,0,0.178,3.344-1.276,3.311c-1.455-0.033-30.507-84.917-66.752-80.957",
            "M 10 10 H 90 V 90 H 10 Z",
            "M 50 0 A 50 50 0 1 0 50 100 A 50 50 0 1 0 50 0",
        ]

        for i in range(self.ITERATIONS):
            svg_path = paths[i % len(paths)]
            p = canvas_pyr.Path2D(svg_path)

    def test_save_png(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / f"canvas-stress-test-{time.time()}.png"
            canvas = canvas_pyr.createCanvas(128, 128)
            ctx = canvas.getContext("2d")
            for i in range(self.ITERATIONS):
                ctx.fillStyle = f"rgb({i % 256}, {(i * 3) % 256}, {(i * 7) % 256})"
                ctx.fillRect(0, 0, 128, 128)
                ctx.strokeStyle = "white"
                ctx.strokeRect(10, 10, 108, 108)

                canvas.savePng(str(tmp_path))

    def test_encode_various_image_formats(self):
        canvas = canvas_pyr.createCanvas(128, 128)
        ctx = canvas.getContext("2d")
        for i in range(self.ITERATIONS):
            ctx.fillStyle = f"hsl({i % 360}, 70%, 50%)"
            ctx.fillRect(0, 0, 128, 128)

            png = canvas.encode("png")
            self.assertGreater(len(png), 0)

            jpeg = canvas.encode("jpeg", 80)
            self.assertGreater(len(jpeg), 0)

            webp = canvas.encode("webp", 80)
            self.assertGreater(len(webp), 0)

    def test_exif_jpeg_decode(self):
        exif_jpeg = self._test_path("fixtures", "with-exif.jpg").read_bytes()

        for i in range(self.ITERATIONS):
            image = canvas_pyr.Image()
            image.load(exif_jpeg)
            # Draw the decoded image to verify it's valid
            canvas = canvas_pyr.createCanvas(int(image.width), int(image.height))
            ctx = canvas.getContext("2d")
            ctx.drawImage(image, 0, 0)

    def test_combined_interleaved_operations(self):
        exif_jpeg = self._test_path("fixtures", "with-exif.jpg").read_bytes()
        svg_data = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64">'
            + '<circle cx="32" cy="32" r="30" fill="green"/></svg>'
        ).encode("utf-8")

        for i in range(self.ITERATIONS):
            # Path2D from string
            path = canvas_pyr.Path2D("M 0 0 L 50 50 L 100 0 Z")

            # Canvas pattern from canvas
            src_canvas = canvas_pyr.createCanvas(64, 64)
            src_ctx = src_canvas.getContext("2d")
            src_ctx.fillStyle = "blue"
            src_ctx.fill(path)

            dst_canvas = canvas_pyr.createCanvas(256, 256)
            dst_ctx = dst_canvas.getContext("2d")
            pattern = dst_ctx.createPattern(src_canvas, "repeat")
            dst_ctx.fillStyle = pattern
            dst_ctx.fillRect(0, 0, 256, 256)

            # Encode
            dst_canvas.encode("png")

            # SVG canvas
            svg_canvas = canvas_pyr.createCanvas(
                128, 128, canvas_pyr.SvgExportFlag.ConvertTextToPaths
            )
            svg_ctx = svg_canvas.getContext("2d")
            svg_ctx.fillRect(0, 0, 128, 128)
            svg_canvas.width = 64
            svg_canvas.getContent()

            # SVG image decode
            svg_img = canvas_pyr.Image()
            svg_img.load(svg_data)

            # EXIF decode
            exif_img = canvas_pyr.Image()
            exif_img.load(exif_jpeg)
            dst_ctx.drawImage(exif_img, 0, 0, 256, 256)

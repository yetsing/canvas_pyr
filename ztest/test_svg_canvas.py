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


class SVGCanvasTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.canvas = canvas_pyr.createCanvas(
            1024, 768, canvas_pyr.SvgExportFlag.ConvertTextToPaths
        )
        self._load_ava_snapshot("svg-canvas.spec.ts.md")

    def test_adjust_size(self):
        canvas = self.canvas
        canvas.width = 512
        canvas.height = 384

        self.assertEqual(canvas.width, 512)
        self.assertEqual(canvas.height, 384)

    def test_export_path_arc_rect(self):
        canvas = self.canvas
        ctx = canvas.getContext("2d")
        ctx.fillStyle = "yellow"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.lineWidth = 3
        ctx.strokeStyle = "hotpink"
        ctx.strokeRect(50, 450, 100, 100)
        ctx.fillStyle = "hotpink"
        ctx.arc(500, 120, 90, 0, math.pi * 2)
        ctx.fill()
        self._ava_snapshot(
            "should be able to export path/arc/rect",
            canvas.getContent().decode("utf-8"),
        )

    def test_export_text(self):
        font_path = self._test_path("fonts-dir", "iosevka-curly-regular.woff2")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path), "i-curly")
        canvas = self.canvas
        ctx = canvas.getContext("2d")
        ctx.fillStyle = "yellow"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.lineWidth = 3
        ctx.strokeStyle = "hotpink"
        ctx.font = "50px i-curly"
        ctx.strokeText("@napi-rs/canvas", 50, 300)
        self._ava_snapshot(
            "should be able to export text", canvas.getContent().decode("utf-8")
        )

import sys
from pathlib import Path

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import BaseTestCase


class HSLARegressionTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.canvas = canvas_pyr.createCanvas(200, 200)
        self.ctx = self.canvas.getContext("2d")

    def test_hsla_regression(self):
        ctx = self.ctx

        # Test HSLA color parsing
        # hsla(252, 0%, 35%, 0.926) should be equivalent to rgba(89, 89, 89, 0.926)
        ctx.fillStyle = "hsla(252, 0%, 35%, 0.926)"
        ctx.fillRect(20, 20, 80, 80)

        # Equivalent RGBA test for comparison
        value = round((35 / 100) * 255)
        ctx.fillStyle = f"rgba({value}, {value}, {value}, 0.926)"
        ctx.fillRect(120, 20, 80, 80)

        self._snapshot("hsla-regression")

    def test_hsla_color_formats(self):
        ctx = self.ctx

        # Test various HSLA formats
        ctx.fillStyle = "hsl(120, 50%, 50%)"
        ctx.fillRect(10, 10, 40, 40)

        ctx.fillStyle = "hsla(240, 100%, 50%, 0.5)"
        ctx.fillRect(60, 10, 40, 40)

        ctx.fillStyle = "hsla(0, 100%, 50%, 1.0)"
        ctx.fillRect(110, 10, 40, 40)

        self._snapshot("hsla-color-formats")

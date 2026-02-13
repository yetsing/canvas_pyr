import platform
import sys
from pathlib import Path

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import BaseTestCase


class SVGTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        font_path = self._test_path("fonts", "iosevka-slab-regular.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path))

        self._fixture = self._test_path("text.svg").read_text(encoding="utf-8")

    def test_convert_svg_text_to_path(self):
        result = canvas_pyr.convertSVGTextToPath(self._fixture)
        output_path = self._test_path("text-to-path.svg")
        output = output_path.read_text(encoding="utf-8")
        if platform.system() == "Windows":
            self.skipTest("Skip on windows")
        else:
            result = result.decode("utf-8")
            for got, want in zip(result.splitlines(), output.splitlines()):
                self.assertEqual(got.strip(), want.strip())

import sys
from pathlib import Path

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import BaseTestCase


class VariableFontsTestCase(BaseTestCase):
    def test_has_variations_with_non_variable_fonts(self):
        # Load a standard font
        font_path = self._test_path("fonts", "iosevka-regular.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path), "Iosevka")

        # Check if it has variations (it shouldn't for a non-variable font)
        has_variations = canvas_pyr.GlobalFonts.hasVariations("Iosevka", 400, 5, 0)
        self.assertFalse(has_variations)

    def test_get_variation_axes_with_non_variable_fonts(self):
        # Load a standard font
        font_path = self._test_path("fonts", "iosevka-regular.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path), "Iosevka")

        # Get variation axes (should return an empty list for non-variable fonts)
        axes = canvas_pyr.GlobalFonts.getVariationAxes("Iosevka", 400, 5, 0)
        self.assertEqual(axes, [])

    def test_has_variations_with_variable_fonts(self):
        # Load a variable font
        font_path = self._test_path("fonts", "Oswald.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path), "Oswald")

        # Check if it has variations (it should for a variable font)
        has_variations = canvas_pyr.GlobalFonts.hasVariations("Oswald", 400, 5, 0)
        self.assertTrue(has_variations)

    def test_get_variation_axes_with_variable_fonts(self):
        # Load a variable font
        font_path = self._test_path("fonts", "Oswald.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path), "Oswald")

        # Get variation axes (should return a list of axes for variable fonts)
        axes = canvas_pyr.GlobalFonts.getVariationAxes("Oswald", 400, 5, 0)
        self.assertTrue(len(axes) > 0)

        weight_axis = next(
            (axis for axis in axes if axis.tag == 0x77676874), None
        )  # 'wght'
        self.assertIsNotNone(weight_axis)
        if weight_axis:
            self.assertEqual(weight_axis.min, 200)
            self.assertEqual(weight_axis.max, 700)
            self.assertEqual(weight_axis.def_, 400)

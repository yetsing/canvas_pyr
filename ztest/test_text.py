import platform
import sys
from pathlib import Path

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import BaseTestCase


class TextTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.canvas = canvas_pyr.createCanvas(512, 512)
        self.ctx = self.canvas.getContext("2d")

        font_path = self._test_path("fonts", "iosevka-slab-regular.ttf")
        self.assertTrue(
            canvas_pyr.GlobalFonts.registerFromPath(str(font_path)),
            "Register Iosevka font failed",
        )

    def test_align_center(self):
        canvas = self.canvas
        ctx = self.ctx
        x = canvas.width / 2
        ctx.strokeStyle = "black"
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.stroke()
        ctx.textAlign = "center"
        ctx.font = "16px Iosevka Slab"
        ctx.fillText("Hello Canvas", x, 200)
        self._snapshot("text-align-center")

    def test_align_end(self):
        canvas = self.canvas
        ctx = self.ctx
        x = canvas.width / 2
        ctx.strokeStyle = "black"
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.stroke()
        ctx.textAlign = "end"
        ctx.font = "16px Iosevka Slab"
        ctx.fillText("Hello Canvas", x, 200)
        self._snapshot("text-align-end")

    def test_align_left(self):
        canvas = self.canvas
        ctx = self.ctx
        x = canvas.width / 2
        ctx.strokeStyle = "black"
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.stroke()
        ctx.textAlign = "left"
        ctx.font = "16px Iosevka Slab"
        ctx.fillText("Hello Canvas", x, 200)
        self._snapshot("text-align-left")

    def test_align_right(self):
        canvas = self.canvas
        ctx = self.ctx
        x = canvas.width / 2
        ctx.strokeStyle = "black"
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.stroke()
        ctx.textAlign = "right"
        ctx.font = "16px Iosevka Slab"
        ctx.fillText("Hello Canvas", x, 200)
        self._snapshot("text-align-right")

    def test_align_start(self):
        canvas = self.canvas
        ctx = self.ctx
        x = canvas.width / 2
        ctx.strokeStyle = "black"
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.stroke()
        ctx.textAlign = "start"
        ctx.font = "16px Iosevka Slab"
        ctx.fillText("Hello Canvas", x, 200)
        self._snapshot("text-align-start")

    def test_fill_text_line_break_as_space(self):
        canvas = self.canvas
        ctx = self.ctx
        x = canvas.width / 2
        ctx.font = "16px Iosevka Slab"
        ctx.fillText("Hello\nCanvas", x, 200)
        self._snapshot("fillText-line-break-as-space")

    def _register_font(self, *parts, family=None):
        path = self._test_path("fonts", *parts)
        ok = (
            canvas_pyr.GlobalFonts.registerFromPath(str(path), family)
            if family
            else canvas_pyr.GlobalFonts.registerFromPath(str(path))
        )
        self.assertTrue(ok, f"Register font failed: {path}")

    def _draw_direction_align_test(
        self, ctx, *, text=None, max_width=None, letter_spacing="3px"
    ):
        canvas = ctx.canvas
        x = canvas.width / 2

        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.strokeStyle = "green"
        ctx.stroke()

        ctx.font = "48px Science Gothic"
        ctx.fillStyle = "black"
        ctx.letterSpacing = letter_spacing

        def get_text(dir_, align):
            return text or f"{dir_} {align}!"

        ctx.direction = "ltr"
        ctx.fillText(get_text("ltr", "start"), 0, 50, max_width)
        ctx.direction = "inherit"
        ctx.textAlign = "left"
        ctx.fillText(get_text("ltr", "left"), 0, 100, max_width)

        ctx.textAlign = "center"
        ctx.fillText(get_text("ltr", "center"), x, 150, max_width)

        ctx.textAlign = "end"
        ctx.fillText(get_text("ltr", "end"), canvas.width, 200, max_width)
        ctx.textAlign = "right"
        ctx.fillText(get_text("ltr", "right"), canvas.width, 250, max_width)

        ctx.direction = "rtl"
        ctx.textAlign = "start"
        ctx.fillText(get_text("rtl", "start"), canvas.width, 350, max_width)
        ctx.textAlign = "right"
        ctx.fillText(get_text("rtl", "right"), canvas.width, 400, max_width)

        ctx.textAlign = "center"
        ctx.fillText(get_text("rtl", "center"), x, 450, max_width)

        ctx.textAlign = "end"
        ctx.fillText(get_text("rtl", "end"), 0, 500, max_width)
        ctx.textAlign = "left"
        ctx.fillText(get_text("rtl", "left"), 0, 550, max_width)

    def test_stroke_text_line_break_as_space(self):
        canvas = self.canvas
        ctx = self.ctx
        x = canvas.width / 2
        ctx.font = "32px Iosevka Slab"
        ctx.strokeText("Hello\nCanvas", x, 200)
        self._snapshot("strokeText-line-break-as-space")

    def test_measure_text_with_suffix_spaces(self):
        ctx = self.ctx
        ctx.font = "50px Iosevka Slab"
        width = ctx.measureText("Hello").width
        width_with_space = ctx.measureText("hello ").width
        width_with_two_space = ctx.measureText("hello  ").width
        self.assertNotEqual(width, width_with_space)
        self.assertEqual(ctx.measureText(" ").width, width_with_space - width)
        self.assertEqual(ctx.measureText("  ").width, width_with_two_space - width)

    def test_text_baseline(self):
        ctx = self.ctx
        ctx.font = "48px Iosevka Slab"
        ctx.textBaseline = "bottom"
        ctx.fillText("abcdef", 50, 100)
        ctx.fillText("abcdefg", 50, 100)
        self._snapshot("text-baseline")

    def test_text_baseline_all(self):
        ctx = self.ctx
        baselines = ["top", "hanging", "middle", "alphabetic", "ideographic", "bottom"]
        ctx.font = "36px Iosevka Slab"
        ctx.strokeStyle = "red"

        for index, baseline in enumerate(baselines):
            ctx.textBaseline = baseline  # type: ignore
            y = 75 + index * 75
            ctx.beginPath()
            ctx.moveTo(0, y + 0.5)
            ctx.lineTo(550, y + 0.5)
            ctx.stroke()
            ctx.fillText(f"Abcdefghijklmnop ({baseline})", 0, y)

        self._snapshot("text-baseline-all")

    def test_letter_spacing(self):
        canvas = canvas_pyr.createCanvas(800, 800)
        ctx = canvas.getContext("2d")
        ctx.font = "30px Iosevka Slab"

        # Default letter spacing
        ctx.fillText(f"Hello world (default: {ctx.letterSpacing})", 10, 40)

        # Custom letter spacing: 10px
        ctx.letterSpacing = "10px"
        ctx.fillText(f"Hello world ({ctx.letterSpacing})", 10, 90)
        ctx.save()
        # Custom letter spacing: 20px
        ctx.letterSpacing = "20px"
        ctx.fillText(f"Hello world ({ctx.letterSpacing})", 10, 140)
        ctx.restore()
        ctx.fillText(f"Hello world ({ctx.letterSpacing})", 10, 190)

        ctx.textAlign = "center"
        width = ctx.measureText(f"Hello world ({ctx.letterSpacing})").width
        ctx.fillText(f"Hello world ({ctx.letterSpacing})", width / 2 + 10, 240)

        ctx.textAlign = "start"
        ctx.fillText(f"Hello world ({ctx.letterSpacing})", 10, 290)
        ctx.textAlign = "right"
        ctx.fillText(f"Hello world ({ctx.letterSpacing})", -width + 10, 340)

        self._snapshot("letter-spacing", canvas=canvas)

    def test_negative_letter_spacing(self):
        canvas = canvas_pyr.createCanvas(800, 800)
        ctx = canvas.getContext("2d")
        ctx.font = "30px Iosevka Slab"

        # Default letter spacing
        ctx.fillText(f"Hello world (default: {ctx.letterSpacing})", 10, 40)
        ctx.letterSpacing = "-5px"
        ctx.fillText(f"Hello world ({ctx.letterSpacing})", 10, 90)

        self._snapshot("negative-letter-spacing", canvas=canvas)

    def test_word_spacing(self):
        canvas = canvas_pyr.createCanvas(800, 800)
        ctx = canvas.getContext("2d")
        ctx.font = "30px Iosevka Slab"

        # Default word spacing
        ctx.fillText(f"Hello world (default: {ctx.wordSpacing})", 10, 40)

        # Custom word spacing: 10px
        ctx.wordSpacing = "10px"
        ctx.fillText(f"Hello world ({ctx.wordSpacing})", 10, 90)
        ctx.save()
        # Custom word spacing: 20px
        ctx.wordSpacing = "20px"
        ctx.fillText(f"Hello world ({ctx.wordSpacing})", 10, 140)
        ctx.restore()
        ctx.fillText(f"Hello world ({ctx.wordSpacing})", 10, 190)

        ctx.textAlign = "center"
        width = ctx.measureText(f"Hello world ({ctx.wordSpacing})").width
        ctx.fillText(f"Hello world ({ctx.wordSpacing})", width / 2 + 10, 240)

        ctx.textAlign = "start"
        ctx.fillText(f"Hello world ({ctx.wordSpacing})", 10, 290)
        ctx.textAlign = "right"
        ctx.fillText(f"Hello world ({ctx.wordSpacing})", -width + 10, 340)

        self._snapshot("word-spacing", canvas=canvas)

    def test_text_align_with_space(self):
        if platform.system() != "Darwin":
            self.skipTest("Skip test")
            return
        ctx = self.ctx
        ctx.strokeStyle = "black"
        ctx.lineWidth = 1
        ctx.moveTo(100, 0)
        ctx.lineTo(100, 512)
        ctx.stroke()
        ctx.font = "38px Iosevka Slab"
        ctx.textAlign = "center"
        ctx.fillText("Mona Lisa", 100, 50)
        ctx.fillText("A B C", 100, 200)
        self._snapshot("text-align-with-space")

    def test_font_variation_settings(self):
        self._register_font("Oswald.ttf", family="Oswald")
        ctx = self.ctx
        ctx.font = "50px Oswald"
        ctx.fontVariationSettings = "'wght' 700"
        ctx.fillText("Hello World", 50, 100)
        self._snapshot("font-variation-settings")

    def test_font_variation_settings_with_font_family(self):
        self._register_font("RobotoMono-VariableFont_wght.ttf", family="Roboto Mono")
        canvas = canvas_pyr.createCanvas(1280, 680)
        ctx = canvas.getContext("2d")
        ctx.fillStyle = "blue"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = "white"
        for i in range(1, 10):
            ctx.font = f"{i * 100} 45px Roboto Mono"
            ctx.fontVariationSettings = f"'wght' {i * 100}"
            ctx.fillText(
                f"{i * 100}: Jackdaws love my big sphinx of quartz", 30, i * 65
            )
        self._snapshot("font-variation-settings-with-font-family", canvas=canvas)

    def test_font_stretch(self):
        # Inconsolata is a variable font that supports width from 50% to 200%
        self._register_font(
            "Inconsolata-VariableFont_wdth,wght.woff2", family="Inconsolata"
        )
        canvas = canvas_pyr.createCanvas(800, 600)
        ctx = canvas.getContext("2d")
        ctx.font = "30px Inconsolata"

        stretches = [
            "ultra-condensed",
            "extra-condensed",
            "condensed",
            "semi-condensed",
            "normal",
            "semi-expanded",
            "expanded",
            "extra-expanded",
            "ultra-expanded",
        ]
        for index, stretch in enumerate(stretches):
            ctx.fontStretch = stretch  # type: ignore
            ctx.fillText(f"Hello World ({ctx.fontStretch})", 10, 40 + index * 60)

        self._snapshot("font-stretch", canvas=canvas)

    def test_font_kerning(self):
        # Use a serif font that has kerning information
        self._register_font("SourceSerifPro-Regular.ttf", family="Source Serif Pro")
        canvas = canvas_pyr.createCanvas(600, 300)
        ctx = canvas.getContext("2d")
        ctx.font = "48px Source Serif Pro"

        # Test text with common kerning pairs: AV, Ta, We
        test_text = "AVA Ta We"

        # Default (auto)
        ctx.fillText(f"{test_text} (auto)", 10, 60)
        self.assertEqual(ctx.fontKerning, "auto")

        # Kerning normal
        ctx.fontKerning = "normal"
        ctx.fillText(f"{test_text} (normal)", 10, 140)
        self.assertEqual(ctx.fontKerning, "normal")

        # Kerning none - characters should be evenly spread
        ctx.fontKerning = "none"
        ctx.fillText(f"{test_text} (none)", 10, 220)
        self.assertEqual(ctx.fontKerning, "none")

        self._snapshot("font-kerning", canvas=canvas)

    def test_font_stretch_default_value(self):
        self.assertEqual(self.ctx.fontStretch, "normal")

    def test_font_kerning_default_value(self):
        self.assertEqual(self.ctx.fontKerning, "auto")

    def test_font_stretch_invalid_value_ignored(self):
        ctx = self.ctx
        ctx.fontStretch = "condensed"
        self.assertEqual(ctx.fontStretch, "condensed")
        ctx.fontStretch = "invalid-stretch"  # type: ignore
        self.assertEqual(ctx.fontStretch, "condensed")  # Should remain unchanged

    def test_font_kerning_invalid_value_ignored(self):
        ctx = self.ctx
        ctx.fontKerning = "none"
        self.assertEqual(ctx.fontKerning, "none")
        ctx.fontKerning = "invalid-kerning"  # type: ignore
        self.assertEqual(ctx.fontKerning, "none")  # Should remain unchanged

    def test_font_variant_caps_default_value(self):
        self.assertEqual(self.ctx.fontVariantCaps, "normal")

    def test_font_variant_caps_invalid_value_ignored(self):
        ctx = self.ctx
        ctx.fontVariantCaps = "small-caps"
        self.assertEqual(ctx.fontVariantCaps, "small-caps")
        ctx.fontVariantCaps = "invalid-caps"  # type: ignore
        self.assertEqual(ctx.fontVariantCaps, "small-caps")  # Should remain unchanged

    def test_font_variant_caps_all_values(self):
        ctx = self.ctx
        valid_values = [
            "normal",
            "small-caps",
            "all-small-caps",
            "petite-caps",
            "all-petite-caps",
            "unicase",
            "titling-caps",
        ]
        for value in valid_values:
            ctx.fontVariantCaps = value  # type: ignore
            self.assertEqual(ctx.fontVariantCaps, value)

    def test_font_variant_caps(self):
        self._register_font("ScienceGothic-VariableFont.ttf", family="Science Gothic")
        canvas = canvas_pyr.createCanvas(650, 390)
        ctx = canvas.getContext("2d")

        # Set white background
        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = "black"
        ctx.font = "32px Science Gothic"

        # Test text to show caps variants
        test_text = "Hello World 123"

        # Default (normal)
        ctx.fillText(f"{test_text} (normal)", 10, 50)
        self.assertEqual(ctx.fontVariantCaps, "normal")

        # small-caps
        ctx.fontVariantCaps = "small-caps"
        ctx.fillText(f"{test_text} (small-caps)", 10, 100)
        self.assertEqual(ctx.fontVariantCaps, "small-caps")

        # all-small-caps
        ctx.fontVariantCaps = "all-small-caps"
        ctx.fillText(f"{test_text} (all-small-caps)", 10, 150)
        self.assertEqual(ctx.fontVariantCaps, "all-small-caps")

        # petite-caps
        ctx.fontVariantCaps = "petite-caps"
        ctx.fillText(f"{test_text} (petite-caps)", 10, 200)
        self.assertEqual(ctx.fontVariantCaps, "petite-caps")

        # all-petite-caps
        ctx.fontVariantCaps = "all-petite-caps"
        ctx.fillText(f"{test_text} (all-petite-caps)", 10, 250)
        self.assertEqual(ctx.fontVariantCaps, "all-petite-caps")

        # unicase
        ctx.fontVariantCaps = "unicase"
        ctx.fillText(f"{test_text} (unicase)", 10, 300)
        self.assertEqual(ctx.fontVariantCaps, "unicase")

        # titling-caps
        ctx.fontVariantCaps = "titling-caps"
        ctx.fillText(f"{test_text} (titling-caps)", 10, 350)
        self.assertEqual(ctx.fontVariantCaps, "titling-caps")

        self._snapshot("font-variant-caps", canvas=canvas)

    def test_font_variant_caps_from_css_font_shorthand(self):
        self._register_font("ScienceGothic-VariableFont.ttf", family="Science Gothic")
        canvas = canvas_pyr.createCanvas(620, 200)
        ctx = canvas.getContext("2d")

        # Set white background
        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = "black"

        # Test font shorthand with small-caps
        ctx.font = "small-caps 36px Science Gothic"
        self.assertEqual(ctx.fontVariantCaps, "small-caps")
        ctx.fillText("Hello World(small-caps)", 10, 50)

        # Setting font without small-caps should reset fontVariantCaps to normal
        ctx.font = "36px Science Gothic"
        self.assertEqual(ctx.fontVariantCaps, "normal")
        ctx.fillText("Hello World(normal)", 10, 110)

        # Setting font with normal variant explicitly
        ctx.font = "normal 36px Science Gothic"
        self.assertEqual(ctx.fontVariantCaps, "normal")
        ctx.fillText("Hello World(normal explicit)", 10, 170)

        self._snapshot("font-variant-caps-from-css-font-shorthand", canvas=canvas)

    def test_font_variant_caps_shorthand_vs_property_equality(self):
        self._register_font("ScienceGothic-VariableFont.ttf", family="Science Gothic")

        canvas1 = canvas_pyr.createCanvas(500, 100)
        ctx1 = canvas1.getContext("2d")
        ctx1.fillStyle = "white"
        ctx1.fillRect(0, 0, canvas1.width, canvas1.height)
        ctx1.fillStyle = "black"
        ctx1.font = "small-caps 36px Science Gothic"
        ctx1.fillText("Hello World ABC xyz", 10, 60)

        canvas2 = canvas_pyr.createCanvas(500, 100)
        ctx2 = canvas2.getContext("2d")
        ctx2.fillStyle = "white"
        ctx2.fillRect(0, 0, canvas2.width, canvas2.height)
        ctx2.fillStyle = "black"
        ctx2.font = "36px Science Gothic"
        ctx2.fontVariantCaps = "small-caps"
        ctx2.fillText("Hello World ABC xyz", 10, 60)

        buffer1 = canvas1.encode("png")
        buffer2 = canvas2.encode("png")
        self.assertEqual(buffer1, buffer2)

    def test_direction_all_values(self):
        ctx = self.ctx
        for value in ["ltr", "rtl", "inherit"]:
            ctx.direction = value  # type: ignore
            if value == "inherit":
                self.assertEqual(ctx.direction, "ltr")
            else:
                self.assertEqual(ctx.direction, value)

    def test_direction_letter_spacing(self):
        canvas = canvas_pyr.createCanvas(600, 360)
        ctx = canvas.getContext("2d")
        self._register_font("ScienceGothic-VariableFont.ttf", family="Science Gothic")
        x = canvas.width / 2

        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.strokeStyle = "green"
        ctx.stroke()

        ctx.font = "45px Science Gothic"
        ctx.fillStyle = "black"
        ctx.letterSpacing = "20px"

        ctx.fillText("Hi!", x, 50)
        ctx.direction = "rtl"
        ctx.fillText("Hi!", x, 130)

        ctx.letterSpacing = "12.832px"
        ctx.fillText("Hello world!", x, 210, 236.21)
        ctx.direction = "ltr"
        ctx.fillText("Hello world!", x, 280, 236.21)

        self._snapshot("direction-letter-spacing", canvas=canvas)

    def test_direction_align(self):
        canvas = canvas_pyr.createCanvas(500, 580)
        ctx = canvas.getContext("2d")
        self._register_font("ScienceGothic-VariableFont.ttf", family="Science Gothic")
        self._draw_direction_align_test(ctx, letter_spacing="3px")
        self._snapshot("direction-align", canvas=canvas)

    def test_direction_align_max_width(self):
        canvas = canvas_pyr.createCanvas(500, 580)
        ctx = canvas.getContext("2d")
        self._register_font("ScienceGothic-VariableFont.ttf", family="Science Gothic")
        self._draw_direction_align_test(
            ctx, text="Hello!", max_width=160, letter_spacing="20px"
        )
        self._snapshot("direction-align-max-width", canvas=canvas)

    def test_direction_save_restore(self):
        canvas = canvas_pyr.createCanvas(400, 160)
        ctx = canvas.getContext("2d")
        self._register_font("ScienceGothic-VariableFont.ttf", family="Science Gothic")

        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        ctx.font = "38px Science Gothic"
        ctx.fillStyle = "black"

        ctx.fillText(f"direction: {ctx.direction}", 0, 50)

        ctx.save()
        ctx.direction = "rtl"
        ctx.fillText(f"direction: {ctx.direction}", canvas.width, 90)
        ctx.restore()

        ctx.fillText(f"direction: {ctx.direction}", 0, 130)

        self.assertEqual(ctx.direction, "ltr")
        self._snapshot("direction-save-restore", canvas=canvas)

    def test_direction_stroke_letter_spacing(self):
        canvas = canvas_pyr.createCanvas(500, 260)
        ctx = canvas.getContext("2d")
        self._register_font("SourceSerifPro-Regular.ttf", family="Source Serif Pro")
        x = canvas.width / 2

        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.strokeStyle = "green"
        ctx.stroke()

        ctx.font = "38px Source Serif Pro"
        ctx.letterSpacing = "10px"

        ctx.direction = "ltr"
        ctx.fillStyle = "black"
        ctx.fillText("LTR text", x, 50)
        ctx.strokeStyle = "blue"
        ctx.lineWidth = 1.5
        ctx.strokeText("LTR text", x, 100)

        ctx.direction = "rtl"
        ctx.fillStyle = "black"
        ctx.fillText("RTL text", x, 170)
        ctx.strokeStyle = "red"
        ctx.strokeText("RTL text", x, 220)

        self._snapshot("direction-stroke-letter-spacing", canvas=canvas)

    def test_direction_negative_letter_spacing(self):
        canvas = canvas_pyr.createCanvas(500, 200)
        ctx = canvas.getContext("2d")
        self._register_font("ScienceGothic-VariableFont.ttf", family="Science Gothic")
        x = canvas.width / 2

        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        ctx.beginPath()
        ctx.moveTo(x, 0)
        ctx.lineTo(x, canvas.height)
        ctx.strokeStyle = "green"
        ctx.stroke()

        ctx.font = "40px Science Gothic"
        ctx.fillStyle = "black"
        ctx.letterSpacing = "-5px"

        ctx.direction = "ltr"
        ctx.fillText("Negative", x, 60)

        ctx.direction = "rtl"
        ctx.fillText("Negative", x, 140)

        self._snapshot("direction-negative-letter-spacing", canvas=canvas)

    def test_direction_measure_text(self):
        canvas = canvas_pyr.createCanvas(400, 100)
        ctx = canvas.getContext("2d")
        self._register_font("ScienceGothic-VariableFont.ttf", family="Science Gothic")

        ctx.font = "38px Science Gothic"

        text_no_spaces = "Hello"
        ctx.direction = "ltr"
        ltr_metrics1 = ctx.measureText(text_no_spaces)
        ctx.direction = "rtl"
        rtl_metrics1 = ctx.measureText(text_no_spaces)
        self.assertEqual(ltr_metrics1.width, rtl_metrics1.width)

        text_with_spaces = "Hello World!"
        ctx.direction = "ltr"
        ltr_metrics2 = ctx.measureText(text_with_spaces)
        ctx.direction = "rtl"
        rtl_metrics2 = ctx.measureText(text_with_spaces)
        self.assertEqual(ltr_metrics2.width, rtl_metrics2.width)

        text_trailing_space = "  Hello World "
        ctx.direction = "ltr"
        ltr_metrics3 = ctx.measureText(text_trailing_space)
        ctx.direction = "rtl"
        rtl_metrics3 = ctx.measureText(text_trailing_space)
        self.assertEqual(ltr_metrics3.width, rtl_metrics3.width)

    def test_cursive_scripts(self):
        canvas = canvas_pyr.createCanvas(650, 300)
        ctx = canvas.getContext("2d")
        self._register_font("Harmattan-Regular.ttf", family="Harmattan")

        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = "black"
        ctx.font = "50px Harmattan"

        ctx.fillText("مرحبا بالعالم", 0, 50)
        ctx.fillText("English مرحبا بالعالم", 0, 110)

        ctx.direction = "rtl"
        ctx.fillText("مرحبا بالعالم", canvas.width, 200)
        ctx.fillText("English مرحبا بالعالم", canvas.width, 260)

        self._snapshot("cursive-scripts", canvas=canvas)

    def test_cursive_scripts_ignore_letter_spacing(self):
        canvas = canvas_pyr.createCanvas(680, 600)
        ctx = canvas.getContext("2d")
        self._register_font("Harmattan-Regular.ttf", family="Harmattan")
        self._register_font("NotoSansMongolian-Regular.ttf", family="Mongolian")
        self._register_font("NotoSansNKo-Regular.ttf", family="NKo")

        end = canvas.width
        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, end, canvas.height)
        ctx.fillStyle = "black"
        ctx.font = "50px Mongolian, NKo, Harmattan"

        ctx.letterSpacing = "26px"
        ctx.wordSpacing = "18px"

        # Arabic Script: "Hello World"
        ctx.fillText("مرحبا بالعالم", 0, 50)
        # N’Ko Script: "Hello World"
        ctx.fillText("ߌ ߣߌ߫ ߖߐ߫ ߘߎߢߊ߫", 0, 120)
        # Mongolian Script
        ctx.fillText("ᠺᠣᠮᠫᠢᠦ᠋ᠲ᠋ᠧᠷ", 0, 190)

        ctx.direction = "rtl"
        ctx.fillText("مرحبا بالعالم", end, 260)
        ctx.fillText("ߌ ߣߌ߫ ߖߐ߫ ߘߎߢߊ߫", end, 330)
        ctx.fillText("ᠺᠣᠮᠫᠢᠦ᠋ᠲ᠋ᠧᠷ", end, 400)

        ctx.fillText("English مرحبا بالعالم", end, 500)
        ctx.direction = "ltr"
        ctx.fillText("English مرحبا بالعالم", 0, 570)

        self._snapshot("cursive-scripts-ignore-letter-spacing", canvas=canvas)

    def test_lang_default_value(self):
        self.assertEqual(self.ctx.lang, "inherit")

    def test_lang_accepts_bcp47_tags(self):
        ctx = self.ctx
        tags = ["en", "en-US", "zh-Hans", "zh-Hant", "ja", "ko", "ar", "he"]
        for tag in tags:
            ctx.lang = tag
            self.assertEqual(ctx.lang, tag)

    def test_lang_save_restore(self):
        ctx = self.ctx
        self.assertEqual(ctx.lang, "inherit")

        ctx.lang = "tr"
        self.assertEqual(ctx.lang, "tr")

        ctx.save()
        ctx.lang = "en-US"
        self.assertEqual(ctx.lang, "en-US")

        ctx.restore()
        self.assertEqual(ctx.lang, "tr")

    def test_lang_ligature_turkish_vs_english(self):
        self._register_font("Lato-Regular.ttf", family="Lato")
        canvas = canvas_pyr.createCanvas(450, 150)
        ctx = canvas.getContext("2d")

        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = "black"
        ctx.font = "36px Lato"

        ctx.lang = "en"
        ctx.fillText("en: finish crafting", 20, 55)

        ctx.lang = "tr"
        ctx.fillText("tr: finish crafting", 20, 115)

        self._snapshot("lang-ligature-turkish-vs-english", canvas=canvas)

    def test_text_rendering_default_value(self):
        self.assertEqual(self.ctx.textRendering, "auto")

    def test_text_rendering_all_values(self):
        ctx = self.ctx
        valid_values = [
            "auto",
            "optimizeSpeed",
            "optimizeLegibility",
            "geometricPrecision",
        ]
        for value in valid_values:
            ctx.textRendering = value  # type: ignore
            self.assertEqual(ctx.textRendering, value)

    def test_text_rendering_invalid_value_ignored(self):
        ctx = self.ctx
        ctx.textRendering = "optimizeSpeed"
        self.assertEqual(ctx.textRendering, "optimizeSpeed")
        ctx.textRendering = "invalid-rendering"  # type: ignore
        self.assertEqual(ctx.textRendering, "optimizeSpeed")  # Should remain unchanged

    def test_text_rendering_save_restore(self):
        ctx = self.ctx
        self.assertEqual(ctx.textRendering, "auto")

        ctx.textRendering = "optimizeLegibility"
        self.assertEqual(ctx.textRendering, "optimizeLegibility")

        ctx.save()
        ctx.textRendering = "optimizeSpeed"
        self.assertEqual(ctx.textRendering, "optimizeSpeed")

        ctx.restore()
        self.assertEqual(
            ctx.textRendering, "optimizeLegibility"
        )  # Should remain unchanged

    def test_text_rendering_comparison(self):
        self._register_font("SourceSerifPro-Regular.ttf", family="Source Serif Pro")
        canvas = canvas_pyr.createCanvas(800, 400)
        ctx = canvas.getContext("2d")

        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = "black"
        ctx.font = "28px Source Serif Pro"

        test_text = "office waffle"
        modes = ["auto", "optimizeSpeed", "optimizeLegibility", "geometricPrecision"]

        widths = {}
        for index, mode in enumerate(modes):
            ctx.textRendering = mode  # type: ignore
            widths[mode] = ctx.measureText(test_text).width
            ctx.fillText(f"{mode}: {test_text}", 20, 60 + index * 80)

        self.assertGreaterEqual(widths["optimizeSpeed"], widths["auto"])
        self.assertEqual(widths["auto"], widths["optimizeLegibility"])
        self.assertEqual(widths["auto"], widths["geometricPrecision"])

        self._snapshot("text-rendering-comparison", canvas=canvas)

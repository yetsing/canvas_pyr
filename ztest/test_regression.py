import math
import platform
import sys
import unittest
from pathlib import Path

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import BaseTestCase


class RegressionTestCase(BaseTestCase):
    def test_transform_with_state(self):
        canvas = canvas_pyr.createCanvas(256, 256)
        ctx = canvas.getContext("2d")
        ctx.translate(128.5, 128.5)
        ctx.scale(1, 1)
        ctx.clearRect(-128, -128, 256, 256)
        ctx.beginPath()
        ctx.moveTo(-52.5, -38.5)
        ctx.lineTo(52.5, -38.5)
        ctx.lineTo(52.5, 38.5)
        ctx.lineTo(-52.5, 38.5)
        ctx.lineTo(-52.5, -38.5)
        ctx.closePath()
        ctx.save()
        p = ctx.createLinearGradient(0, 0, 0, 77)
        p.addColorStop(1, "rgba(0, 128, 128, 1)")
        p.addColorStop(0.6, "rgba(0, 255, 255, 1)")
        p.addColorStop(0.3, "rgba(176, 199, 45, 1)")
        p.addColorStop(0.0, "rgba(204, 82, 51, 1)")
        ctx.fillStyle = p
        ctx.transform(1, 0, 0, 1, -52.5, -38.5)
        ctx.transform(1, 0, 0, 1, 0, 0)
        ctx.fill()
        ctx.restore()
        self._snapshot("transform-with-state", canvas=canvas)

    def test_transform_with_radial_gradient(self):
        canvas = canvas_pyr.createCanvas(256, 256)
        ctx = canvas.getContext("2d")
        ctx.translate(128.5, 128.5)
        ctx.scale(1, 1)
        ctx.clearRect(-128, -128, 256, 256)
        ctx.beginPath()
        ctx.save()
        ctx.transform(1, 0, 0, 0.9090909090909091, 0, 0)
        ctx.arc(0, 0, 110, 0, math.tau, False)
        ctx.restore()
        ctx.save()
        p = ctx.createRadialGradient(0.5, 0.5, 0, 0.2, 0.4, 0.5)
        p.addColorStop(1, "rgba(0, 0, 255, 1)")
        p.addColorStop(0, "rgba(200, 200, 200, 0)")
        ctx.fillStyle = p
        ctx.transform(220, 0, 0, 200, -110, -100)
        ctx.transform(1, 0, 0, 1, 0, 0)
        ctx.fill()
        ctx.restore()
        self._snapshot("transform-with-radial-gradient", canvas=canvas)

    def test_transform_with_radial_gradient_x(self):
        if platform.machine().lower().startswith(("arm", "aarch")):
            self.skipTest("skip on arm")
        canvas = canvas_pyr.createCanvas(400, 282)
        ctx = canvas.getContext("2d")
        ctx.translate(200.5, 141.5)
        ctx.scale(1, 1)
        ctx.clearRect(-181.5, -128, 363, 256)
        ctx.beginPath()
        ctx.save()
        ctx.transform(1, 0, 0, 0.5555555555555556, 0, 0)
        ctx.arc(0, 0, 180, 0, math.tau, False)
        ctx.restore()
        ctx.save()
        p = ctx.createRadialGradient(0.5, 0.5, 0, 0.5, 0.5, 0.5)
        p.addColorStop(1, "rgba(0, 0, 255, 1)")
        p.addColorStop(0, "rgba(200, 200, 200, 0)")
        ctx.fillStyle = p
        ctx.transform(360, 0, 0, 200, -180, -100)
        ctx.transform(1, 0, 0, 1, 0, 0)
        ctx.fill()
        ctx.restore()
        self._snapshot("transform-with-radial-gradient-x", canvas=canvas)

    def test_fill_alpha_should_not_affect_draw_image(self):
        canvas = canvas_pyr.createCanvas(300, 320)
        ctx = canvas.getContext("2d")
        ctx.fillStyle = "rgba(3, 169, 244, 0.5)"

        # Image
        image = self._load_image("javascript.png")
        ctx.drawImage(image, 0, 0, 200, 100)
        self._snapshot("fill-alpha-should-not-effect-drawImage", "png", canvas=canvas)

    def test_global_alpha_should_effect_draw_image(self):
        canvas = canvas_pyr.createCanvas(300, 320)
        ctx = canvas.getContext("2d")
        ctx.globalAlpha = 0.2

        # Image
        image = self._load_image("javascript.png")
        ctx.drawImage(image, 0, 0, 200, 100)
        self._snapshot("global-alpha-should-effect-drawImage", "png", canvas=canvas)

    def test_draw_text_max_width(self):
        font_path = self._test_path("fonts", "iosevka-slab-regular.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path))
        canvas = canvas_pyr.createCanvas(150, 150)
        ctx = canvas.getContext("2d")
        pad = 10  # padding
        ctx.textBaseline = "top"
        ctx.font = "50px Iosevka Slab"

        ctx.fillRect(0, 0, canvas.width, canvas.height)

        ctx.fillStyle = "blue"
        ctx.fillRect(pad, pad, canvas.width - 2 * pad, canvas.height - 2 * pad)

        max_width = canvas.width - 2 * pad
        ctx.fillStyle = "white"
        ctx.fillText("Short text", pad, 10, max_width)
        ctx.fillText(f"Very {'long ' * 2} text", pad, 80, max_width)
        self._snapshot("draw-text-maxWidth", "png", canvas=canvas)

    def test_draw_text_right_max_width(self):
        font_path = self._test_path("fonts", "iosevka-slab-regular.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path))
        canvas = canvas_pyr.createCanvas(500, 100)
        ctx = canvas.getContext("2d")
        padding = 50
        max_width = canvas.width - padding * 2
        # The background
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = "blue"
        ctx.fillRect(padding, 0, max_width, canvas.height)
        ctx.font = "16px Iosevka Slab"
        ctx.textAlign = "right"
        ctx.fillStyle = "white"
        ctx.textBaseline = "top"
        # Short text
        ctx.fillText("Short text", canvas.width - padding, 10, max_width)
        # Very long text (10 repetitions)
        ctx.fillText(f"Very {'long ' * 10} text", canvas.width - padding, 30, max_width)
        # Very long text (20 repetitions)
        ctx.fillText(f"Very {'long ' * 20} text", canvas.width - padding, 50, max_width)
        self._snapshot("draw-text-right-maxWidth", "png", canvas=canvas)

    def test_draw_text_center_max_width(self):
        font_path = self._test_path("fonts", "iosevka-slab-regular.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path))
        canvas = canvas_pyr.createCanvas(500, 100)
        ctx = canvas.getContext("2d")
        padding = 50
        max_width = canvas.width - padding * 2
        # The background
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = "blue"
        ctx.fillRect(padding, 0, max_width, canvas.height)
        ctx.font = "16px Iosevka Slab"
        ctx.textAlign = "center"
        ctx.fillStyle = "white"
        ctx.textBaseline = "top"
        # Short text
        ctx.fillText("Short text", canvas.width / 2, 10, max_width)
        # Very long text (10 repetitions)
        ctx.fillText(f"Very {'long ' * 10} text", canvas.width / 2, 30, max_width)
        # Very long text (20 repetitions)
        ctx.fillText(f"Very {'long ' * 20} text", canvas.width / 2, 50, max_width)
        self._snapshot("draw-text-center-maxWidth", "png", canvas=canvas)

    def test_draw_svg_with_text(self):
        font_path = self._test_path("fonts", "iosevka-slab-regular.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path))
        canvas = canvas_pyr.createCanvas(1200, 700)
        ctx = canvas.getContext("2d")
        vite_city_gradient = ctx.createLinearGradient(0, 0, 1200, 0)
        vite_city_gradient.addColorStop(0, "#3494e6")
        vite_city_gradient.addColorStop(1, "#EC6EAD")
        ctx.fillStyle = vite_city_gradient
        ctx.fillRect(0, 0, 1200, 700)
        ctx.fillStyle = "white"
        ctx.font = "48px Iosevka Slab"
        title = "@napi-rs/image"
        ctx.fillText(title, 80, 100)

        arrow = self._load_image("image-og.svg")
        ctx.drawImage(arrow, 80, 60)
        different_ratio = 0.3
        if (
            platform.machine().lower() == "x64"
            and platform.system().lower() != "darwin"
        ):
            different_ratio = 0.15
        self._snapshot("draw-svg-with-text", "png", different_ratio, canvas=canvas)

    def test_dom_matrix_transform_point(self):
        point = canvas_pyr.DOMPoint(1, 2)
        matrix = canvas_pyr.DOMMatrix()
        got = matrix.transformPoint(point)
        self.assertEqual(got, point)

    def test_dom_matrix_invert_self_should_return_self_for_non_invertible_matrix(self):
        # Test invertible matrix - should modify this and return this
        invertible_matrix = canvas_pyr.DOMMatrix([2, 0, 0, 2, 10, 10])
        original_invertible = invertible_matrix
        result1 = invertible_matrix.invertSelf()

        self.assertIs(result1, original_invertible)
        self.assertEqual(invertible_matrix.a, 0.5)
        self.assertEqual(invertible_matrix.e, -5)

        # Test non-invertible matrix - should set to NaN and return this (not undefined)
        non_invertible_matrix = canvas_pyr.DOMMatrix([0, 0, 0, 0, 100, 200])
        original_non_invertible = non_invertible_matrix
        result2 = non_invertible_matrix.invertSelf()

        self.assertIs(result2, original_non_invertible)
        self.assertTrue(math.isnan(non_invertible_matrix.a))
        self.assertFalse(non_invertible_matrix.is2D)

    def test_is_point_in_path_with_translate(self):
        canvas = canvas_pyr.createCanvas(1200, 700)
        ctx = canvas.getContext("2d")
        ctx.translate(10, 10)
        ctx.rect(0, 0, 100, 100)
        self.assertFalse(ctx.isPointInPath(0, 0))
        self.assertTrue(ctx.isPointInPath(10, 10))
        self.assertTrue(ctx.isPointInPath(100, 100))
        self.assertTrue(ctx.isPointInPath(110, 110))

    def test_restore_from_scale_zero(self):
        canvas = canvas_pyr.createCanvas(1200, 700)
        ctx = canvas.getContext("2d")
        ctx.scale(0, 0)
        ctx.save()
        ctx.restore()

    def test_shadow_blur_with_translate(self):
        font_path = self._test_path("fonts", "iosevka-slab-regular.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path))
        canvas = canvas_pyr.createCanvas(500, 500)
        ctx = canvas.getContext("2d")
        ctx.font = "48px Iosevka Slab"
        ctx.shadowColor = "rgb(255, 0, 0)"
        ctx.shadowBlur = 10
        ctx.translate(50, 50)
        ctx.fillText("TEST", 0, 0)
        ctx.strokeRect(-50, -50, 200, 100)
        self._snapshot("shadow-blur-with-translate", "png", canvas=canvas)

    def test_shadow_blur_zero_with_text(self):
        font_path = self._test_path("fonts", "iosevka-slab-regular.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path))
        canvas = canvas_pyr.createCanvas(500, 500)
        ctx = canvas.getContext("2d")
        ctx.font = "48px Iosevka Slab"
        ctx.shadowBlur = 0
        ctx.shadowOffsetX = 20
        ctx.shadowOffsetY = 20
        ctx.shadowColor = "red"
        ctx.fillStyle = "green"
        ctx.fillText("TEST", 100, 100)
        self._snapshot("shadow-blur-zero-with-text", "png", canvas=canvas)

    def test_put_image_data_double_free(self):
        canvas = canvas_pyr.createCanvas(1920, 1080)
        ctx = canvas.getContext("2d")

        canvas2 = canvas_pyr.createCanvas(1640, 480)
        ctx2 = canvas2.getContext("2d")
        ctx2.fillStyle = "white"
        ctx2.fillRect(0, 0, canvas2.width, canvas2.height)

        img_data = ctx2.getImageData(0, 0, canvas2.width, canvas2.height)

        ctx.putImageData(img_data, 0, 0, 0, 0, canvas.width, canvas.height)

    def test_draw_canvas_on_canvas(self):
        back_canvas = canvas_pyr.createCanvas(1920, 1080)
        back_ctx = back_canvas.getContext("2d")

        pic_canvas = canvas_pyr.createCanvas(640, 480)
        pic_ctx = pic_canvas.getContext("2d")

        back_ctx.fillStyle = "#000000"
        back_ctx.fillRect(0, 0, 1920, 1080)

        # load images from disk or from a URL
        cat_image = self._load_image("javascript.png")

        pic_ctx.drawImage(cat_image, 0, 0, cat_image.width, cat_image.height)

        back_ctx.drawImage(pic_canvas, 240, 0, 1440, 1080)

        self._snapshot("draw-canvas-on-canvas", "png", canvas=back_canvas)

    def test_transform_with_non_inverted_matrix(self):
        canvas = canvas_pyr.createCanvas(100, 100)
        ctx = canvas.getContext("2d")
        ctx.transform(0, 0, 0, 0, 1019, 1165)

    def test_draw_avif_image(self):
        canvas = canvas_pyr.createCanvas(1920, 1080)
        ctx = canvas.getContext("2d")
        image = self._load_image2("fixtures", "issue-996.avif")
        ctx.drawImage(image, 0, 0)
        self._snapshot("draw-avif-image", "png", canvas=canvas)

    def test_canvas_pattern_1010(self):
        canvas = canvas_pyr.createCanvas(512, 512)
        tmp_canvas = canvas_pyr.createCanvas(512, 512)
        ctx = canvas.getContext("2d")
        tmp_ctx = tmp_canvas.getContext("2d")
        image = self._load_image("javascript.png")
        tmp_ctx.drawImage(image, 0, 0)
        pattern = ctx.createPattern(image, "repeat")
        pattern2 = ctx.createPattern(tmp_canvas, "repeat")
        ctx.fillStyle = pattern
        ctx.fillRect(0, 0, 512 / 2, 512)

        ctx.fillStyle = pattern2
        ctx.fillRect(512 / 2, 0, 512 / 2, 512)
        self._snapshot("canvas-pattern-1010", "png", canvas=canvas)

    # @unittest.skip("test fail problem is complex, needs investigation")
    def test_canvas_pattern_should_capture_state_at_creation_1106(self):
        width = 200
        height = 150

        canvas = canvas_pyr.createCanvas(width, height)
        context = canvas.getContext("2d")
        tmp_canvas = canvas_pyr.createCanvas(width, height)
        tmp_context = tmp_canvas.getContext("2d")

        # Create initial red pattern
        tmp_context.fillStyle = "red"
        tmp_context.fillRect(0, 0, width, height)

        pattern = tmp_context.createPattern(tmp_canvas, "no-repeat")

        # Modify the tmp_canvas after pattern creation
        tmp_canvas.width = int(width / 2)
        tmp_canvas.height = int(height / 2)
        tmp_context.fillStyle = "blue"
        tmp_context.fillRect(0, 0, width / 2, height / 2)

        pattern2 = tmp_context.createPattern(tmp_canvas, "no-repeat")

        # Fill with the first pattern (should still be red, not affected by blue changes)
        context.fillStyle = pattern
        context.fillRect(width / 2, height / 2, width / 2, height / 2)

        # Fill with the second pattern (should be blue)
        context.fillStyle = pattern2
        context.fillRect(0, 0, width / 2, height / 2)

        self._snapshot(
            "canvas-pattern-should-capture-state-at-creation-1106", canvas=canvas
        )

    @unittest.skip("python do not convert int to str automatically, but in js it can")
    def test_draw_non_string_text(self):
        font_path = self._test_path("fonts", "iosevka-slab-regular.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path))
        canvas = canvas_pyr.createCanvas(300, 300)
        ctx = canvas.getContext("2d")
        ctx.font = "36px Iosevka Slab"
        ctx.fillStyle = "red"
        with self.assertRaises(TypeError):
            ctx.fillText(2015, 100, 100)  # type: ignore
        with self.assertRaises(TypeError):
            ctx.measureText(2015)  # type: ignore
        self._snapshot("draw-non-string-text", "png", canvas=canvas)

    def test_scale_svg_image(self):
        font_path = self._test_path("fonts", "iosevka-slab-regular.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path))
        image = self._load_image("image-og.svg")
        image.width = image.naturalWidth * 2
        image.height = image.naturalHeight * 2
        canvas = canvas_pyr.createCanvas(int(image.width), int(image.height))
        ctx = canvas.getContext("2d")
        ctx.drawImage(image, 0, 0)
        self._snapshot("scale-svg-image", "png", canvas=canvas)

    def test_shadow_alpha_with_global_alpha(self):
        canvas = canvas_pyr.createCanvas(200, 100)
        ctx = canvas.getContext("2d")

        # Fill with white background
        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, 200, 100)

        # Set globalAlpha to 1 (full opacity)
        ctx.globalAlpha = 1

        # Set shadow with semi-transparent black
        ctx.shadowColor = "rgba(0, 0, 0, 0.5)"
        ctx.shadowBlur = 10
        ctx.shadowOffsetX = 5
        ctx.shadowOffsetY = 5

        # Draw a rectangle with shadow
        ctx.fillStyle = "blue"
        ctx.fillRect(20, 20, 60, 40)

        self._snapshot("shadow-alpha-with-global-alpha", "png", canvas=canvas)

    def test_shadow_clipping_beyond_canvas_bounds(self):
        font_path = self._test_path("fonts", "iosevka-slab-regular.ttf")
        canvas_pyr.GlobalFonts.registerFromPath(str(font_path))
        canvas = canvas_pyr.createCanvas(200, 200)
        ctx = canvas.getContext("2d")

        # Fill with white background
        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, 200, 200)

        # Test 1: Rectangle near right edge with shadow extending beyond canvas
        ctx.shadowColor = "rgba(255, 0, 0, 0.8)"
        ctx.shadowBlur = 20
        ctx.shadowOffsetX = 30
        ctx.shadowOffsetY = 10
        ctx.fillStyle = "blue"
        ctx.fillRect(
            160, 50, 30, 30
        )  # Rectangle positioned so shadow extends beyond right edge

        # Reset shadow for next shape
        ctx.shadowColor = "transparent"
        ctx.shadowBlur = 0
        ctx.shadowOffsetX = 0
        ctx.shadowOffsetY = 0

        # Test 2: Circle near bottom edge with shadow extending beyond canvas
        ctx.shadowColor = "rgba(0, 255, 0, 0.8)"
        ctx.shadowBlur = 15
        ctx.shadowOffsetX = 10
        ctx.shadowOffsetY = 25
        ctx.fillStyle = "purple"
        ctx.beginPath()
        ctx.arc(100, 170, 20, 0, 2 * math.pi)
        ctx.fill()

        # Reset shadow for text
        ctx.shadowColor = "transparent"
        ctx.shadowBlur = 0
        ctx.shadowOffsetX = 0
        ctx.shadowOffsetY = 0

        # Test 3: Text near top edge with shadow extending beyond canvas
        ctx.shadowColor = "rgba(0, 0, 255, 0.8)"
        ctx.shadowBlur = 10
        ctx.shadowOffsetX = 5
        ctx.shadowOffsetY = -15
        ctx.fillStyle = "black"
        ctx.font = "16px Iosevka Slab"
        ctx.fillText(
            "Shadow Test", 50, 20
        )  # Text positioned so shadow extends beyond top edge

        # Reset shadow for stroke test
        ctx.shadowColor = "transparent"
        ctx.shadowBlur = 0
        ctx.shadowOffsetX = 0
        ctx.shadowOffsetY = 0

        # Test 4: Stroke near left edge with shadow extending beyond canvas
        ctx.shadowColor = "rgba(255, 255, 0, 0.8)"
        ctx.shadowBlur = 12
        ctx.shadowOffsetX = -20
        ctx.shadowOffsetY = 5
        ctx.strokeStyle = "red"
        ctx.lineWidth = 3
        ctx.strokeRect(
            10, 110, 40, 40
        )  # Rectangle positioned so shadow extends beyond left edge

        self._snapshot("shadow-clipping-beyond-canvas-bounds", "png", canvas=canvas)

    @unittest.skip(
        "python will throw error when setLineDash receive invalid input, but in js it will not"
    )
    def test_pass_invalid_args_to_set_line_dash_should_not_throw(self):
        canvas = canvas_pyr.createCanvas(100, 100)
        ctx = canvas.getContext("2d")
        ctx.setLineDash([float("nan"), 10])  # Invalid input, but should not throw
        ctx.setLineDash(
            [
                {"cmd": "n"},
                {"cmd": "n"},
            ]  # type: ignore
        )  # type: ignore

    def test_shadow_offset_with_transform(self):
        canvas = canvas_pyr.createCanvas(300, 300)
        ctx = canvas.getContext("2d")

        # Fill with white background
        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, 300, 300)

        # Apply transform - scale down by 0.5 and translate
        ctx.transform(0.5, 0, 0, 0.5, 100, 100)

        # Set shadow properties
        ctx.shadowColor = "rgba(0, 0, 0, 1)"
        ctx.shadowBlur = 0
        ctx.shadowOffsetX = 5
        ctx.shadowOffsetY = 5

        # Draw green rectangle
        ctx.fillStyle = "green"
        ctx.rect(0, 0, 100, 100)
        ctx.fill()

        # The shadow should be offset by exactly 5px in both X and Y directions
        # in device/screen coordinates, regardless of the transform applied
        self._snapshot("shadow-offset-with-transform", "png", canvas=canvas)

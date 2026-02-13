import base64
import math
import os
import pathlib
import sys
import unittest
from io import BytesIO
from pathlib import Path
from typing import Literal, Optional

from PIL import Image

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import BaseTestCase, snapshot_image, upstream_dir


def drawTranslate(ctx: canvas_pyr.CanvasRenderingContext2D):
    # Moved square
    ctx.translate(110, 30)
    ctx.fillStyle = "red"
    ctx.fillRect(0, 0, 80, 80)

    # Reset current transformation matrix to the identity matrix
    ctx.setTransform(1, 0, 0, 1, 0, 0)

    # Unmoved square
    ctx.fillStyle = "gray"
    ctx.fillRect(0, 0, 80, 80)


class DrawTestCase(BaseTestCase):
    """
    Test cases for drawing operations on the canvas.
    """

    def setUp(self) -> None:
        super().setUp()
        self.canvas = canvas_pyr.createCanvas(512, 512)
        self.ctx = self.canvas.getContext("2d")
        basepath = upstream_dir / "__test__"
        self.assertTrue((basepath / "fonts" / "osrs-font-compact.otf").exists())
        self.assertTrue(
            canvas_pyr.GlobalFonts.registerFromPath(
                str(basepath / "fonts" / "osrs-font-compact.otf")
            ),
            "Register osrs-font-compact.otf failed",
        )
        self.assertTrue(
            canvas_pyr.GlobalFonts.registerFromPath(
                str(basepath / "fonts" / "iosevka-slab-regular.ttf")
            ),
            "Register iosevka-slab-regular.ttf failed",
        )
        self.assertTrue(
            canvas_pyr.GlobalFonts.registerFromPath(
                str(basepath / "fonts" / "SourceSerifPro-Regular.ttf")
            ),
            "Register SourceSerifPro-Regular.ttf failed",
        )

    def test_alpha_false(self):
        canvas = canvas_pyr.createCanvas(512, 512)
        ctx = canvas.getContext("2d", {"alpha": False})
        snapshot_image(self, "alpha-false", canvas)

    def test_arc(self):
        ctx = self.ctx
        ctx.beginPath()
        ctx.arc(100, 75, 50, 0, 2 * math.pi)
        ctx.stroke()
        self._snapshot("arc")

    def test_arc_to(self):
        ctx = self.ctx
        ctx.beginPath()
        ctx.moveTo(180, 90)
        ctx.arcTo(180, 130, 110, 130, 130)
        ctx.lineTo(110, 130)
        ctx.stroke()
        self._snapshot("arcTo")

    def test_arc_to_colorful(self):
        ctx = self.ctx
        ctx.beginPath()
        ctx.strokeStyle = "gray"
        ctx.moveTo(200, 20)
        ctx.lineTo(200, 130)
        ctx.lineTo(50, 20)
        ctx.stroke()

        # Arc
        ctx.beginPath()
        ctx.strokeStyle = "black"
        ctx.lineWidth = 5
        ctx.moveTo(200, 20)
        ctx.arcTo(200, 130, 50, 20, 40)
        ctx.stroke()

        # Start point
        ctx.beginPath()
        ctx.fillStyle = "blue"
        ctx.arc(200, 20, 5, 0, 2 * math.pi)
        ctx.fill()

        # Control points
        ctx.beginPath()
        ctx.fillStyle = "red"
        ctx.arc(200, 130, 5, 0, 2 * math.pi)  # Control point one
        ctx.arc(50, 20, 5, 0, 2 * math.pi)  # Control point two
        ctx.fill()

        self._snapshot("arcTo-colorful")

    def test_begin_path(self):
        ctx = self.ctx
        ctx.beginPath()
        ctx.strokeStyle = "blue"
        ctx.moveTo(20, 20)
        ctx.lineTo(200, 20)
        ctx.stroke()

        # Second path
        ctx.beginPath()
        ctx.strokeStyle = "green"
        ctx.moveTo(20, 20)
        ctx.lineTo(120, 120)
        ctx.stroke()
        self._snapshot("beginPath")

    def test_bezier_curve_to(self):
        ctx = self.ctx
        ctx.beginPath()
        ctx.moveTo(30, 30)
        ctx.bezierCurveTo(120, 160, 180, 10, 220, 140)
        ctx.stroke()
        self._snapshot("bezierCurveTo")

    def test_bezier_curve_to_colorful(self):
        ctx = self.ctx
        start = {"x": 50, "y": 20}
        cp1 = {"x": 230, "y": 30}
        cp2 = {"x": 150, "y": 80}
        end = {"x": 250, "y": 100}

        # Cubic Bézier curve
        ctx.beginPath()
        ctx.moveTo(start["x"], start["y"])
        ctx.bezierCurveTo(cp1["x"], cp1["y"], cp2["x"], cp2["y"], end["x"], end["y"])
        ctx.stroke()

        # Start and end points
        ctx.fillStyle = "blue"
        ctx.beginPath()
        ctx.arc(start["x"], start["y"], 5, 0, 2 * math.pi)
        ctx.arc(end["x"], end["y"], 5, 0, 2 * math.pi)
        ctx.fill()

        # Control points
        ctx.fillStyle = "red"
        ctx.beginPath()
        ctx.arc(cp1["x"], cp1["y"], 5, 0, 2 * math.pi)
        ctx.arc(cp2["x"], cp2["y"], 5, 0, 2 * math.pi)
        ctx.fill()

        self._snapshot("bezierCurveTo-colorful")

    def test_clear_rect(self):
        ctx = self.ctx
        canvas = self.canvas
        ctx.beginPath()
        ctx.fillStyle = "#ff6"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # Draw blue triangle
        ctx.beginPath()
        ctx.fillStyle = "blue"
        ctx.moveTo(20, 20)
        ctx.lineTo(180, 20)
        ctx.lineTo(130, 130)
        ctx.closePath()
        ctx.fill()

        # Clear part of the canvas
        ctx.clearRect(10, 10, 120, 100)
        self._snapshot("clearRect")

    def test_clear_rect_full_canvas_optimization(self):
        ctx = self.ctx
        canvas = self.canvas

        # Draw multiple shapes to accumulate layers
        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, 200, 200)
        ctx.fillStyle = "green"
        ctx.fillRect(200, 0, 200, 200)
        ctx.fillStyle = "blue"
        ctx.fillRect(0, 200, 200, 200)

        # Full canvas clear with identity transform - should reset layers
        ctx.clearRect(0, 0, canvas.width, canvas.height)

        # Draw new content
        ctx.fillStyle = "purple"
        ctx.fillRect(150, 150, 200, 200)

        self._snapshot("clearRect-full-canvas-optimization")

    def test_clear_rect_with_transform_preserves_outside(self):
        ctx = self.ctx
        canvas = self.canvas

        # Draw background
        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # Apply transform - clear won't cover everything
        ctx.translate(100, 100)

        # Clear "full canvas" but transform means it doesn't cover everything
        ctx.clearRect(0, 0, canvas.width, canvas.height)

        # The red area at top-left (0,0 to 100,100) should still be visible
        self._snapshot("clearRect-with-transform-preserves-outside")

    def test_clear_rect_with_clip_preserves_outside(self):
        ctx = self.ctx
        canvas = self.canvas

        # Draw background
        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # Aply clip to center region
        ctx.beginPath()
        ctx.rect(100, 100, 300, 300)
        ctx.clip()

        # Clear "full canvas" but clip limits it
        ctx.clearRect(0, 0, canvas.width, canvas.height)

        # The red border around the clip should still be visible
        self._snapshot("clearRect-with-clip-preserves-outside")

    def test_clear_rect_with_pending_save_preserves_state(self):
        ctx = self.ctx
        canvas = self.canvas
        # Test that clearRect with pending save states doesn't use the optimization
        # This ensures the save/restore stack remains consistent

        # Draw backgound
        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # Save state and set up clip
        ctx.save()
        ctx.beginPath()
        ctx.rect(100, 100, 300, 300)
        ctx.clip()

        # Draw inside clip
        ctx.fillStyle = "green"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        #  Full canvas clear while inside save - should NOT reset layers (has pending save)
        #  The clear should only affect the clipped area
        ctx.clearRect(0, 0, canvas.width, canvas.height)

        # Draw new content inside clip
        ctx.fillStyle = "blue"
        ctx.fillRect(150, 150, 200, 200)

        # Restore state - should work correctly
        ctx.restore()

        # Draw outside clip area to verify restore worked
        ctx.fillStyle = "yellow"
        ctx.fillRect(0, 0, 50, 50)

        # Expected: red border (not cleared due to clip), blue square (inside clip),
        # yellow square at top-left (after restore)
        self._snapshot("clearRect-with-pending-save-preserves-state")

    def test_clip(self):
        ctx = self.ctx
        canvas = self.canvas
        # Create circular clipping region
        ctx.beginPath()
        ctx.arc(100, 75, 50, 0, math.pi * 2)
        ctx.clip()

        # Draw stuff that gets clipped
        ctx.fillStyle = "blue"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = "orange"
        ctx.fillRect(0, 0, 100, 100)
        self._snapshot("clip")

    def test_clip_cumulative(self):
        ctx = self.ctx
        canvas = self.canvas
        # Per Canvas2D spec, multiple clip() calls should intersect with each other
        # First clip: left half of the canvas (0 to 256)
        ctx.beginPath()
        ctx.rect(0, 0, 256, 512)
        ctx.clip()

        # Second clip: right half of the canvas (128 to 512)
        # The intersection should be the middle strip (128 to 256)
        ctx.beginPath()
        ctx.rect(128, 0, 384, 512)
        ctx.clip()

        # Fill the entire canvas - only the intersection area (128-256) should be visible
        ctx.fillStyle = "blue"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        self._snapshot("clip-cumulative")

    def test_clip_cumulative_with_layer_promotion(self):
        ctx = self.ctx
        canvas = self.canvas
        # This test verifies that cumulative clip state is correctly preserved
        # across layer promotions (triggered by getImageData).
        # Regression test for: clip state divergence when op() intersection is tracked

        ctx.fillStyle = "lightgray"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        ctx.save()

        # First clip: left portion (0 to 300)
        ctx.beginPath()
        ctx.rect(0, 0, 300, 512)
        ctx.clip()

        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # Trigger layer promotion
        ctx.getImageData(0, 0, 1, 1)

        # Second clip: overlapping region (150 to 450)
        # The cumulative clip should be (150 to 300)
        ctx.beginPath()
        ctx.rect(150, 0, 300, 512)
        ctx.clip()

        # Trigger another layer promotion - clip state must be preserved correctly
        ctx.getImageData(0, 0, 1, 1)

        # Fill with blue - should only appear in the intersection (150 to 300)
        ctx.fillStyle = "blue"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        ctx.restore()

        # After restore, clip should be removed
        # Draw green rectangle outside the previous clip area to verify
        ctx.fillStyle = "green"
        ctx.fillRect(350, 100, 100, 100)

        self._snapshot("clip-cumulative-with-layer-promotion")

    def test_clip_state_consistency_multiple_promotions(self):
        ctx = self.ctx
        canvas = self.canvas
        # Regression test for: clip state divergence when path intersection operation fails
        # This test verifies that clip state remains consistent across multiple layer
        # promotions, even when clips are applied between promotions.

        ctx.fillStyle = "lightgray"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        ctx.save()

        # First clip: left region (0-250)
        ctx.beginPath()
        ctx.rect(0, 0, 250, 512)
        ctx.clip()

        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # Trigger layer promotion
        ctx.getImageData(0, 0, 1, 1)

        # Second clip: overlapping region (100-350)
        # Cumulative clip should be (100-250)
        ctx.beginPath()
        ctx.rect(100, 0, 250, 512)
        ctx.clip()

        ctx.fillStyle = "orange"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # Trigger layer promotion again
        ctx.getImageData(0, 0, 1, 1)

        # Third clip: further narrowing (150-400)
        # Cumulative clip should be (150-250)
        ctx.beginPath()
        ctx.rect(150, 0, 250, 512)
        ctx.clip()

        # Trigger layer promotion a third time
        ctx.getImageData(0, 0, 1, 1)

        # Final fill - should only appear in (150-250) if state is consistent
        ctx.fillStyle = "blue"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        ctx.restore()

        # After restore, no clip - draw marker to verify restore worked
        ctx.fillStyle = "green"
        ctx.fillRect(400, 100, 100, 100)

        # Expected visual:
        # - Gray background
        # - Red strip at 0-100 (first clip only, before second clip)
        # - Orange strip at 100-150 (first + second clip, before third clip)
        # - Blue strip at 150-250 (all three clips)
        # - Green square at 400-500 (after restore)
        self._snapshot("clip-state-consistency-multiple-promotions")

    def test_clip_no_divergence_after_promotion(self):
        ctx = self.ctx
        canvas = self.canvas
        # This test verifies that clip state does NOT diverge between the tracked state
        # and the actual canvas clip after layer promotion.
        # The bug was: canvas had OLD∩NEW but tracked state had OLD after promotion.

        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # Apply first clip
        ctx.beginPath()
        ctx.rect(50, 50, 200, 200)
        ctx.clip()

        # Draw red - should be clipped to 50-250
        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # Layer promotion
        ctx.getImageData(0, 0, 1, 1)

        # Apply second clip - intersection should be 100-250 horizontally
        ctx.beginPath()
        ctx.rect(100, 50, 200, 200)
        ctx.clip()

        # Layer promotion
        ctx.getImageData(0, 0, 1, 1)

        # Draw blue - if state diverged, this would show in wrong region
        ctx.fillStyle = "blue"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # Layer promotion again - this is where divergence would cause problems
        ctx.getImageData(0, 0, 1, 1)

        # Draw green - should STILL be clipped to intersection (100-250)
        # If there was divergence, this might show in wrong region
        ctx.fillStyle = "green"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # The final result should show:
        # - White background
        # - Red region at x=50-100 (first clip only, before second)
        # - Green region at x=100-250 (intersection of both clips)
        self._snapshot("clip-no-divergence-after-promotion")

    def test_close_path(self):
        ctx = self.ctx
        ctx.beginPath()
        ctx.moveTo(20, 140)  # Move pen to bottom-left corner
        ctx.lineTo(120, 10)  # Line to top corner
        ctx.lineTo(220, 140)  # Line to bottom-right corner
        ctx.closePath()  # Line to bottom-left corner
        ctx.stroke()
        self._snapshot("closePath")

    def test_close_path_arc(self):
        ctx = self.ctx
        ctx.beginPath()
        ctx.arc(240, 20, 40, 0, math.pi)
        ctx.moveTo(100, 20)
        ctx.arc(60, 20, 40, 0, math.pi)
        ctx.moveTo(215, 80)
        ctx.arc(150, 80, 65, 0, math.pi)
        ctx.closePath()
        ctx.lineWidth = 6
        ctx.stroke()
        self._snapshot("closePath-arc")

    def test_create_image_data(self):
        ctx = self.ctx
        imageData = ctx.createImageData(256, 256)
        data = imageData.data
        # Iterate through every pixel
        for i in range(0, len(data), 4):
            # Modify pixel data
            data[i + 0] = 190  # R value
            data[i + 1] = 0  # G value
            data[i + 2] = 210  # B value
            data[i + 3] = 255  # A value
        # Draw image data to the canvas
        ctx.putImageData(imageData, 20, 20)
        self._snapshot("createImageData")

    def test_create_linear_gradient(self):
        ctx = self.ctx
        # Add three color stops
        gradient = ctx.createLinearGradient(20, 0, 220, 0)
        gradient.addColorStop(0, "green")
        gradient.addColorStop(0.5, "cyan")
        gradient.addColorStop(1, "green")
        # Set the fill style and draw a rectangle
        ctx.fillStyle = gradient
        ctx.fillRect(20, 20, 200, 100)
        self._snapshot("createLinearGradient")

    def test_create_pattern_no_transform(self):
        ctx = self.ctx
        image = canvas_pyr.Image()
        image_path = str(self._test_path("canvas_createpattern.png"))
        image.load(image_path)
        pattern = ctx.createPattern(image, "repeat")
        ctx.fillStyle = pattern
        ctx.fillRect(0, 0, 300, 300)
        self._snapshot("createPattern-no-transform")

    def test_create_pattern_no_transform_imagedata(self):
        ctx = self.ctx
        image_path = str(self._test_path("canvas_createpattern.png"))
        image = Image.open(image_path).convert("RGBA")
        image_data = canvas_pyr.ImageData(image.tobytes(), image.width, image.height)
        pattern = ctx.createPattern(image_data, "repeat")
        ctx.fillStyle = pattern
        ctx.fillRect(0, 0, 300, 300)
        self._snapshot("createPattern-no-transform-imagedata")

    def test_create_pattern_with_transform(self):
        ctx = self.ctx
        image = canvas_pyr.Image()
        image_path = str(self._test_path("canvas_createpattern.png"))
        image.load(image_path)
        pattern = ctx.createPattern(image, "repeat")
        matrix = canvas_pyr.DOMMatrix()
        pattern.setTransform(matrix.rotate(-45).scale(1.5))
        ctx.fillStyle = pattern
        ctx.fillRect(0, 0, 300, 300)
        self._snapshot("createPattern-with-transform")

    def test_create_radial_gradient(self):
        ctx = self.ctx
        gradient = ctx.createRadialGradient(110, 90, 30, 100, 100, 70)

        # Add three color stops
        gradient.addColorStop(0, "pink")
        gradient.addColorStop(0.9, "white")
        gradient.addColorStop(1, "green")

        # Set the fill style and draw a rectangle
        ctx.fillStyle = gradient
        ctx.fillRect(20, 20, 160, 160)
        self._snapshot("createRadialGradient")

    def test_create_conic_gradient(self):
        ctx = self.ctx
        gradient = ctx.createConicGradient(0, 100, 100)

        # Add five color stops
        gradient.addColorStop(0, "red")
        gradient.addColorStop(0.25, "orange")
        gradient.addColorStop(0.5, "yellow")
        gradient.addColorStop(0.75, "green")
        gradient.addColorStop(1, "blue")

        # Set the fill style and draw a rectangle
        ctx.fillStyle = gradient
        ctx.fillRect(20, 20, 200, 200)
        self._snapshot("createConicGradient")

    def test_draw_image(self):
        ctx = self.ctx
        image = canvas_pyr.Image()
        image_path = str(self._test_path("javascript.png"))
        image.load(image_path)
        ctx.drawImage(image, 0, 0)
        self._snapshot("drawImage")

    def test_draw_image_svg(self):
        ctx = self.ctx
        image = canvas_pyr.Image()
        image_path = str(self._test_path("mountain.svg"))
        image.load(image_path)
        ctx.drawImage(image, 0, 0)
        self._snapshot("drawImage-svg")

    def test_draw_image_svg_with_only_viewbox(self):
        ctx = self.ctx
        image = canvas_pyr.Image()
        image_path = str(self._test_path("only-viewbox.svg"))
        image.load(image_path)
        ctx.drawImage(image, 0, 0)
        self._snapshot("drawImage-svg-with-only-viewBox")

    def test_draw_image_svg_resize(self):
        ctx = self.ctx
        image = canvas_pyr.Image()
        image_path = str(self._test_path("resize.svg"))
        image.load(image_path)
        image.width = 100
        image.height = 100
        ctx.drawImage(image, 0, 0)
        snapshot_image(self, "drawImage-svg-resize", self.canvas, "png", 0.2)

    @unittest.skip("upstream skip")
    def test_draw_image_svg_with_css(self):
        ctx = self.ctx
        image = canvas_pyr.Image()
        image_path = self._test_path("css-style.svg")
        image.load(image_path.read_bytes())
        ctx.drawImage(image, 0, 0)
        self._snapshot("drawImage-svg-with-css")

    def test_draw_image_svg_without_width_height_should_be_empty_image(self):
        ctx = self.ctx
        canvas = self.canvas
        svg_path = self._test_path("mountain.svg")
        svg_content = svg_path.read_text(encoding="utf-8")
        image = canvas_pyr.Image()
        svg_data = (
            svg_content.replace('width="128"', "")
            .replace('height="128"', "")
            .encode("utf-8")
        )
        image.load(svg_data)
        ctx.drawImage(image, 0, 0)
        output = canvas.encode("png")
        output_data = Image.open(BytesIO(output)).convert("RGBA")
        self.assertEqual(
            output_data.tobytes(),
            bytes([0]) * (output_data.width * output_data.height * 4),
            "Expected fully transparent image when SVG has no width/height",
        )

    def test_draw_image_svg_noto_emoji(self):
        ctx = self.ctx
        image = self._load_image("notoemoji-person.svg")
        ctx.drawImage(image, 0, 0)
        self._snapshot("draw-image-svg-noto-emoji")

    def test_draw_image_another_canvas(self):
        ctx = self.ctx

        ctx.fillStyle = "hotpink"
        ctx.fillRect(10, 10, 100, 100)

        anotherCanvas = canvas_pyr.createCanvas(200, 200)
        anotherContext = anotherCanvas.getContext("2d")
        anotherContext.beginPath()
        anotherContext.ellipse(80, 80, 50, 75, math.pi / 4, 0, 2 * math.pi)
        anotherContext.stroke()

        anotherContext.beginPath()
        anotherContext.setLineDash([5, 5])
        anotherContext.moveTo(10, 150)
        anotherContext.lineTo(150, 10)
        anotherContext.stroke()

        ctx.drawImage(anotherCanvas, 150, 150)
        self._snapshot("drawImage-another-Canvas")

    def test_draw_image_canvas_with_source_rect(self):
        ctx = self.ctx
        sourceCanvas = canvas_pyr.createCanvas(200, 200)
        sourceCtx = sourceCanvas.getContext("2d")

        # Draw quadrants
        sourceCtx.fillStyle = "red"
        sourceCtx.fillRect(0, 0, 100, 100)
        sourceCtx.fillStyle = "green"
        sourceCtx.fillRect(100, 0, 100, 100)
        sourceCtx.fillStyle = "blue"
        sourceCtx.fillRect(0, 100, 100, 100)
        sourceCtx.fillStyle = "yellow"
        sourceCtx.fillRect(100, 100, 100, 100)

        # Draw only green quadrant scaled up
        ctx.drawImage(sourceCanvas, 100, 0, 100, 100, 50, 50, 200, 200)
        self._snapshot("drawImage-canvas-with-source-rect")

    def test_draw_image_canvas_with_alpha(self):
        ctx = self.ctx
        ctx.fillStyle = "blue"
        ctx.fillRect(0, 0, 512, 512)

        sourceCanvas = canvas_pyr.createCanvas(200, 200)
        sourceCtx = sourceCanvas.getContext("2d")
        sourceCtx.fillStyle = "red"
        sourceCtx.fillRect(0, 0, 200, 200)

        ctx.globalAlpha = 0.5
        ctx.drawImage(sourceCanvas, 150, 150)

        # Higher tolerance (5%) due to cross-platform alpha blending differences:
        # When blending red (255,0,0) at 0.5 alpha over blue (0,0,255), the blue channel
        # calculation is: B = 0 * 0.5 + 255 * 0.5 = 127.5
        # - Linux x86-64 rounds to 127
        # - macOS ARM64 rounds to 126
        # This 1-value difference across the 200x200 blended area causes ~3.8% pixel diff.
        snapshot_image(self, "drawImage-canvas-with-alpha", self.canvas, "png", 5)

    def test_draw_image_canvas_with_transform(self):
        ctx = self.ctx
        sourceCanvas = canvas_pyr.createCanvas(100, 100)
        sourceCtx = sourceCanvas.getContext("2d")
        sourceCtx.fillStyle = "red"
        sourceCtx.fillRect(0, 0, 100, 100)

        ctx.translate(256, 256)
        ctx.rotate(math.pi / 4)
        ctx.drawImage(sourceCanvas, -50, -50)
        self._snapshot("drawImage-canvas-with-transform")

    def test_draw_image_throws_type_error_for_invalid_image_type(self):
        ctx = self.ctx
        with self.assertRaises(TypeError):
            ctx.drawImage({}, 0, 0)  # type: ignore
        with self.assertRaises(TypeError):
            ctx.drawImage(42, 0, 0)  # type: ignore
        with self.assertRaises(TypeError):
            ctx.drawImage("not an image", 0, 0)  # type: ignore
        with self.assertRaises(TypeError):
            ctx.drawImage(None, 0, 0)  # type: ignore

    def test_draw_canvas_basic(self):
        ctx = self.ctx

        # Create source canvas with some drawings
        sourceCanvas = canvas_pyr.createCanvas(200, 200)
        sourceCtx = sourceCanvas.getContext("2d")

        # Draw an ellipse with dashed line (same pattern as drawImage-another-Canvas)
        sourceCtx.beginPath()
        sourceCtx.ellipse(80, 80, 50, 75, math.pi / 4, 0, 2 * math.pi)
        sourceCtx.stroke()

        sourceCtx.beginPath()
        sourceCtx.setLineDash([5, 5])
        sourceCtx.moveTo(10, 150)
        sourceCtx.lineTo(150, 10)
        sourceCtx.stroke()

        # Draw hotpink rect on destination first
        ctx.fillStyle = "hotpink"
        ctx.fillRect(10, 10, 100, 100)

        # Draw source canvas to destination at position (150, 150)
        ctx.drawCanvas(sourceCanvas, 150, 150)
        self._snapshot("drawCanvas-basic")

    def test_draw_canvas_with_scaling(self):
        ctx = self.ctx

        # Create source canvas with a simple shape
        sourceCanvas = canvas_pyr.createCanvas(100, 100)
        sourceCtx = sourceCanvas.getContext("2d")

        # Draw a filled circle
        sourceCtx.fillStyle = "blue"
        sourceCtx.beginPath()
        sourceCtx.arc(50, 50, 40, 0, math.pi * 2)
        sourceCtx.fill()

        # Draw a smaller version at top-left
        ctx.drawCanvas(sourceCanvas, 10, 10, 50, 50)
        # Draw a larger version at center
        ctx.drawCanvas(sourceCanvas, 150, 150, 200, 200)

        self._snapshot("drawCanvas-with-scaling")

    def test_draw_canvas_with_source_rect(self):
        ctx = self.ctx

        # Create source canvas with four colored quadrants
        sourceCanvas = canvas_pyr.createCanvas(200, 200)
        sourceCtx = sourceCanvas.getContext("2d")

        # Draw quadrants
        sourceCtx.fillStyle = "red"
        sourceCtx.fillRect(0, 0, 100, 100)
        sourceCtx.fillStyle = "green"
        sourceCtx.fillRect(100, 0, 100, 100)
        sourceCtx.fillStyle = "blue"
        sourceCtx.fillRect(0, 100, 100, 100)
        sourceCtx.fillStyle = "yellow"
        sourceCtx.fillRect(100, 100, 100, 100)

        # Draw only green quadrant scaled up
        ctx.drawCanvas(sourceCanvas, 100, 0, 100, 100, 50, 50, 200, 200)
        self._snapshot("drawCanvas-with-source-rect")

    def test_draw_canvas_with_alpha(self):
        ctx = self.ctx

        # Fill background with blue
        ctx.fillStyle = "blue"
        ctx.fillRect(0, 0, 512, 512)

        # Create source canvas with red rectangle
        sourceCanvas = canvas_pyr.createCanvas(200, 200)
        sourceCtx = sourceCanvas.getContext("2d")
        sourceCtx.fillStyle = "red"
        sourceCtx.fillRect(0, 0, 200, 200)

        # Draw with 50% alpha
        ctx.globalAlpha = 0.5
        ctx.drawCanvas(sourceCanvas, 150, 150)

        # Higher tolerance (5%) due to cross-platform alpha blending differences
        self._snapshot("drawCanvas-with-alpha", "png", 5)

    def test_draw_canvas_with_transform(self):
        ctx = self.ctx

        # Create source canvas with red square
        sourceCanvas = canvas_pyr.createCanvas(100, 100)
        sourceCtx = sourceCanvas.getContext("2d")
        sourceCtx.fillStyle = "red"
        sourceCtx.fillRect(0, 0, 100, 100)

        # Apply rotation transform
        ctx.translate(256, 256)
        ctx.rotate(math.pi / 4)
        ctx.drawCanvas(sourceCanvas, -50, -50)
        self._snapshot("drawCanvas-with-transform")

    def test_draw_canvas_with_shadow(self):
        ctx = self.ctx

        # Create source canvas with a shape
        sourceCanvas = canvas_pyr.createCanvas(100, 100)
        sourceCtx = sourceCanvas.getContext("2d")
        sourceCtx.fillStyle = "blue"
        sourceCtx.fillRect(10, 10, 80, 80)

        # Set up shadow
        ctx.shadowColor = "rgba(0, 0, 0, 0.5)"
        ctx.shadowBlur = 20
        ctx.shadowOffsetX = 10
        ctx.shadowOffsetY = 10

        # Draw canvas with shadow
        ctx.drawCanvas(sourceCanvas, 100, 100)
        self._snapshot("drawCanvas-with-shadow")

    def test_draw_canvas_complex_vector(self):
        ctx = self.ctx

        # Create source canvas with complex vector graphics
        sourceCanvas = canvas_pyr.createCanvas(200, 200)
        sourceCtx = sourceCanvas.getContext("2d")

        # Draw gradient-filled shape
        gradient = sourceCtx.createLinearGradient(0, 0, 200, 200)
        gradient.addColorStop(0, "red")
        gradient.addColorStop(0.5, "yellow")
        gradient.addColorStop(1, "green")

        sourceCtx.fillStyle = gradient
        sourceCtx.beginPath()
        sourceCtx.moveTo(100, 10)
        sourceCtx.lineTo(190, 190)
        sourceCtx.lineTo(10, 190)
        sourceCtx.closePath()
        sourceCtx.fill()

        # Add stroked circle
        sourceCtx.strokeStyle = "purple"
        sourceCtx.lineWidth = 5
        sourceCtx.beginPath()
        sourceCtx.arc(100, 100, 60, 0, math.pi * 2)
        sourceCtx.stroke()

        # Draw the source canvas at different positions and sizes
        ctx.drawCanvas(sourceCanvas, 10, 10)
        ctx.drawCanvas(sourceCanvas, 250, 10, 100, 100)
        ctx.drawCanvas(sourceCanvas, 10, 250, 150, 150)

        self._snapshot("drawCanvas-complex-vector", "png", 0.3)

    def test_draw_canvas_preserves_vector_quality(self):
        ctx = self.ctx

        # Create a small source canvas with crisp vector graphics
        sourceCanvas = canvas_pyr.createCanvas(50, 50)
        sourceCtx = sourceCanvas.getContext("2d")

        # Draw a precise shape
        sourceCtx.strokeStyle = "black"
        sourceCtx.lineWidth = 2
        sourceCtx.beginPath()
        sourceCtx.moveTo(5, 25)
        sourceCtx.lineTo(25, 5)
        sourceCtx.lineTo(45, 25)
        sourceCtx.lineTo(25, 45)
        sourceCtx.closePath()
        sourceCtx.stroke()

        # Scale up significantly - vector graphics should remain crisp
        ctx.drawCanvas(sourceCanvas, 50, 50, 400, 400)
        self._snapshot("drawCanvas-preserves-vector-quality")

    def test_draw_canvas_preserves_source_transform_after_read(self):
        ctx = self.ctx
        sourceCanvas = canvas_pyr.createCanvas(200, 200)
        sourceCtx = sourceCanvas.getContext("2d")

        # Apply transform to source
        sourceCtx.translate(100, 100)
        sourceCtx.rotate(math.pi / 4)

        # Draw initial content with transform
        sourceCtx.fillStyle = "red"
        sourceCtx.fillRect(-50, -50, 100, 100)

        # Draw source to destination (triggers layer promotion in source)
        ctx.drawCanvas(sourceCanvas, 0, 0)

        # Continue drawing on source - transform should still be active
        sourceCtx.fillStyle = "blue"
        sourceCtx.fillRect(-25, -25, 50, 50)

        # Draw again to verify continued operations work with restored transform
        ctx.drawCanvas(sourceCanvas, 250, 0)
        self._snapshot("drawCanvas-preserves-source-transform-after-read")

    def test_draw_canvas_preserves_source_clip_after_read(self):
        ctx = self.ctx
        sourceCanvas = canvas_pyr.createCanvas(200, 200)
        sourceCtx = sourceCanvas.getContext("2d")

        # Apply circular clip to source
        sourceCtx.beginPath()
        sourceCtx.arc(100, 100, 80, 0, math.pi * 2)
        sourceCtx.clip()

        # Draw initial content (clipped to circle)
        sourceCtx.fillStyle = "red"
        sourceCtx.fillRect(0, 0, 200, 200)

        # Draw source to destination (triggers layer promotion)
        ctx.drawCanvas(sourceCanvas, 0, 0)

        # Continue drawing on source - clip should still be active
        sourceCtx.fillStyle = "blue"
        sourceCtx.fillRect(0, 0, 100, 100)

        # Draw again to verify clip was restored
        ctx.drawCanvas(sourceCanvas, 250, 0)
        self._snapshot("drawCanvas-preserves-source-clip-after-read")

    def test_ellipse(self):
        ctx = self.ctx
        # Draw the ellipse
        ctx.beginPath()
        ctx.ellipse(100, 100, 50, 75, math.pi / 4, 0, 2 * math.pi)
        ctx.stroke()

        # Draw the ellipse's line of reflection
        ctx.beginPath()
        ctx.setLineDash([5, 5])
        ctx.moveTo(0, 200)
        ctx.lineTo(200, 0)
        ctx.stroke()
        self._snapshot("ellipse")

    def test_fill(self):
        ctx = self.ctx
        region = canvas_pyr.Path2D()
        region.moveTo(30, 90)
        region.lineTo(110, 20)
        region.lineTo(240, 130)
        region.lineTo(60, 130)
        region.lineTo(190, 20)
        region.lineTo(270, 90)
        region.closePath()

        # Fill path
        ctx.fillStyle = "green"
        ctx.fill(region, "evenodd")
        self._snapshot("fill")

    def test_fill_rect(self):
        ctx = self.ctx
        ctx.fillStyle = "hotpink"
        ctx.fillRect(20, 10, 150, 100)
        self._snapshot("fillRect")

    def test_fill_text(self):
        ctx = self.ctx
        canvas = self.canvas
        ctx.fillStyle = "yellow"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = "black"
        ctx.font = "48px Iosevka Slab"
        ctx.fillText("skr canvas", 50, 150)
        gradient = ctx.createConicGradient(0, 100, 100)

        # Add five color stops
        gradient.addColorStop(0, "red")
        gradient.addColorStop(0.15, "orange")
        gradient.addColorStop(0.25, "yellow")
        gradient.addColorStop(0.35, "orange")
        gradient.addColorStop(0.5, "green")
        gradient.addColorStop(0.75, "cyan")
        gradient.addColorStop(1, "blue")

        # Set the fill style and draw a rectangle
        ctx.fillStyle = gradient
        ctx.fillText("@napi-rs/canvas", 50, 250)
        self._snapshot("fillText", "png", 0.13)

    def test_fill_text_max_width(self):
        ctx = self.ctx
        canvas = self.canvas
        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = "black"
        ctx.font = "24px Iosevka Slab"
        ctx.fillText("Hello world", 50, 90, 90)
        ctx.fillText("Hello world", 160, 90)
        self._snapshot("fillText-maxWidth", "png", 0.8)

    def test_fill_text_aa(self):
        ctx = self.ctx
        ctx.imageSmoothingEnabled = False
        ctx.font = "16px OSRSFontCompact"
        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, 100, 100)
        ctx.fillStyle = "black"
        ctx.fillText("@napi-rs/canvas", 10, 10)
        ctx.fillText("ABC abc 123", 10, 40)
        self._snapshot("fillText-AA", "png", 3.2)

    def test_fill_text_colrv1(self):
        ctx = self.ctx
        canvas_pyr.GlobalFonts.registerFromPath(
            str(self._test_path("fonts", "COLR-v1.ttf")), "Colrv1"
        )
        ctx.font = "100px Colrv1"
        ctx.fillText("abc", 50, 100)
        self._snapshot("fillText-COLRv1", "png", 0.5)

    def test_get_context_attributes(self):
        default_ctx = self.ctx
        default_attrs = default_ctx.getContextAttributes()
        self.assertEqual(default_attrs.alpha, True)
        self.assertEqual(default_attrs.desynchronized, False)

        canvas = canvas_pyr.createCanvas(512, 512)
        ctx = canvas.getContext("2d", {"alpha": False})
        custom_attrs = ctx.getContextAttributes()
        self.assertEqual(custom_attrs.alpha, False)
        self.assertEqual(custom_attrs.desynchronized, False)

    def test_get_image_data(self):
        ctx = self.ctx
        ctx.rect(10, 10, 100, 100)
        ctx.fill()
        imageData = ctx.getImageData(60, 60, 200, 100)
        ctx.putImageData(imageData, 150, 10)
        self._snapshot("getImageData")

    def test_is_point_in_path(self):
        ctx = self.ctx

        ctx.rect(0, 0, 100, 100)
        self.assertEqual(ctx.isPointInPath(50, -1), False)
        self.assertEqual(ctx.isPointInPath(50, 0), True)
        self.assertEqual(ctx.isPointInPath(50, 1), True)

        ctx.rect(40, 40, 20, 20)
        self.assertEqual(ctx.isPointInPath(50, 50), True)
        self.assertEqual(ctx.isPointInPath(50, 50, "nonzero"), True)
        self.assertEqual(ctx.isPointInPath(50, 50, "evenodd"), False)

        path = canvas_pyr.Path2D()
        path.rect(0, 0, 100, 100)
        self.assertEqual(ctx.isPointInPath(path, 50, -1), False)
        self.assertEqual(ctx.isPointInPath(path, 50, 1), True)

        path.rect(40, 40, 20, 20)
        self.assertEqual(ctx.isPointInPath(path, 50, 50), True)
        self.assertEqual(ctx.isPointInPath(path, 50, 50, "nonzero"), True)
        self.assertEqual(ctx.isPointInPath(path, 50, 50, "evenodd"), False)

    def test_is_point_in_stroke(self):
        ctx = self.ctx
        ctx.rect(10, 10, 100, 100)
        ctx.stroke()
        self.assertEqual(ctx.isPointInStroke(50, 9), False)
        self.assertEqual(ctx.isPointInStroke(50, 10), True)
        self.assertEqual(ctx.isPointInStroke(50, 11), False)

        ctx.lineWidth = 3
        ctx.stroke()
        self.assertEqual(ctx.isPointInStroke(50, 9), True)
        self.assertEqual(ctx.isPointInStroke(50, 10), True)
        self.assertEqual(ctx.isPointInStroke(50, 11), True)

        ctx.lineWidth = 1
        path = canvas_pyr.Path2D()
        path.rect(10, 10, 100, 100)
        self.assertEqual(ctx.isPointInStroke(path, 50, 9), False)
        self.assertEqual(ctx.isPointInStroke(path, 50, 10), True)
        self.assertEqual(ctx.isPointInStroke(path, 50, 11), False)

    def test_line_to(self):
        ctx = self.ctx
        ctx.beginPath()
        ctx.moveTo(30, 50)
        ctx.lineTo(150, 100)
        ctx.stroke()
        self._snapshot("lineTo")

    def test_line_to_with_invalid_point(self):
        ctx = self.ctx
        ctx.beginPath()
        ctx.lineTo(float("nan"), 100)
        ctx.lineTo(50, 50)
        ctx.lineTo(100, float("nan"))
        ctx.lineTo(250, 100)
        ctx.stroke()
        self._snapshot("lineTo-with-invalid-point")

    def test_measure_text(self):
        ctx = self.ctx
        ctx.font = "50px Iosevka Slab"
        metrics = ctx.measureText("@napi-rs/canvas")
        self.assertEqual(metrics.actualBoundingBoxLeft, -3)
        self.assertEqual(metrics.actualBoundingBoxAscent, 42)
        self.assertEqual(metrics.actualBoundingBoxDescent, 10)
        self.assertTrue(abs(metrics.actualBoundingBoxRight - 372) < 0.001)
        ctx.measureText("\u200b")

    def test_measure_text_empty_string_should_not_throw(self):
        ctx = self.ctx
        ctx.font = "50px Iosevka Slab"
        self.assertEqual(
            ctx.measureText("").to_dict(),
            {
                "actualBoundingBoxAscent": 0,
                "actualBoundingBoxDescent": 0,
                "actualBoundingBoxLeft": 0,
                "actualBoundingBoxRight": 0,
                "fontBoundingBoxAscent": 0,
                "fontBoundingBoxDescent": 0,
                "alphabeticBaseline": 0,
                "emHeightAscent": 0,
                "emHeightDescent": 0,
                "width": 0,
            },
        )

    def test_move_to(self):
        ctx = self.ctx
        ctx.beginPath()
        ctx.moveTo(50, 50)
        ctx.lineTo(200, 50)
        ctx.moveTo(50, 90)
        ctx.lineTo(280, 120)
        ctx.stroke()
        self._snapshot("moveTo")

    def test_put_image_data(self):
        ctx = self.ctx

        def putImageData(imageData, dx, dy, dirtyX, dirtyY, dirtyWidth, dirtyHeight):
            data = imageData.data
            height = imageData.height
            width = imageData.width
            dirtyX = dirtyX or 0
            dirtyY = dirtyY or 0
            dirtyWidth = dirtyWidth if dirtyWidth is not None else width
            dirtyHeight = dirtyHeight if dirtyHeight is not None else height
            limitBottom = dirtyY + dirtyHeight
            limitRight = dirtyX + dirtyWidth
            for y in range(dirtyY, limitBottom):
                for x in range(dirtyX, limitRight):
                    pos = y * width + x
                    ctx.fillStyle = f"rgba({data[pos*4+0]},{data[pos*4+1]},{data[pos*4+2]},{data[pos*4+3]/255})"
                    ctx.fillRect(x + dx, y + dy, 1, 1)

        # Draw content onto the canvas
        ctx.fillRect(0, 0, 100, 100)
        # Create an ImageData object from it
        imagedata = ctx.getImageData(0, 0, 100, 100)
        # use the putImageData function that illustrates how putImageData works
        putImageData(imagedata, 150, 0, 50, 50, 25, 25)
        self._snapshot("putImageData")

    def test_quadratic_curve_to(self):
        ctx = self.ctx
        # Quadratic Bézier curve
        ctx.beginPath()
        ctx.moveTo(50, 20)
        ctx.quadraticCurveTo(230, 30, 50, 100)
        ctx.stroke()

        # Start and end points
        ctx.fillStyle = "blue"
        ctx.beginPath()
        ctx.arc(50, 20, 5, 0, 2 * math.pi)
        ctx.arc(50, 100, 5, 0, 2 * math.pi)
        ctx.fill()

        # Control point
        ctx.fillStyle = "red"
        ctx.beginPath()
        ctx.arc(230, 30, 5, 0, 2 * math.pi)
        ctx.fill()
        self._snapshot("quadraticCurveTo")

    def test_rect(self):
        ctx = self.ctx
        ctx.fillStyle = "yellow"
        ctx.rect(10, 20, 150, 100)
        ctx.fill()
        self._snapshot("rect")

    def test_reset_transform(self):
        ctx = self.ctx
        # Skewed rects
        ctx.transform(1, 0, 1.7, 1, 0, 0)
        ctx.fillStyle = "gray"
        ctx.fillRect(40, 40, 50, 20)
        ctx.fillRect(40, 90, 50, 20)

        # Non-skewed rects
        ctx.resetTransform()
        ctx.fillStyle = "red"
        ctx.fillRect(40, 40, 50, 20)
        ctx.fillRect(40, 90, 50, 20)
        self._snapshot("resetTransform")

    def test_reset(self):
        ctx = self.ctx
        # Draw something and change styles
        ctx.fillStyle = "red"
        ctx.strokeStyle = "blue"
        ctx.lineWidth = 5
        ctx.globalAlpha = 0.5
        ctx.shadowColor = "green"
        ctx.shadowBlur = 10
        ctx.shadowOffsetX = 5
        ctx.shadowOffsetY = 5
        ctx.transform(1, 0.2, 0.8, 1, 0, 0)
        # Change font-related properties
        ctx.font = "24px Iosevka Slab"
        ctx.textAlign = "center"
        ctx.textBaseline = "top"
        ctx.direction = "rtl"
        ctx.letterSpacing = "5px"
        ctx.wordSpacing = "10px"
        ctx.fontStretch = "expanded"
        ctx.fontKerning = "none"
        ctx.fontVariationSettings = '"wght" 700'
        ctx.fillRect(50, 50, 100, 100)
        # Save state
        ctx.save()
        ctx.fillStyle = "purple"
        ctx.save()
        # Reset the context
        ctx.reset()

        # Verify all styles are reset to defaults
        self.assertEqual(ctx.fillStyle, "#000000")
        self.assertEqual(ctx.strokeStyle, "#000000")
        self.assertEqual(ctx.lineWidth, 1)
        self.assertEqual(ctx.globalAlpha, 1)
        self.assertEqual(ctx.shadowColor, "#000000")
        self.assertEqual(ctx.shadowBlur, 0)
        self.assertEqual(ctx.shadowOffsetX, 0)
        self.assertEqual(ctx.shadowOffsetY, 0)
        self.assertEqual(ctx.lineCap, "butt")
        self.assertEqual(ctx.lineJoin, "miter")
        self.assertEqual(ctx.miterLimit, 10)
        self.assertEqual(ctx.lineDashOffset, 0)
        self.assertEqual(ctx.getLineDash(), [])
        # Font-related properties
        self.assertEqual(ctx.font, "10px sans-serif")
        self.assertEqual(ctx.textAlign, "start")
        self.assertEqual(ctx.textBaseline, "alphabetic")
        # TODO: Support direction
        # self.assertEqual(ctx.direction, 'rtl')
        self.assertEqual(ctx.letterSpacing, "0px")
        self.assertEqual(ctx.wordSpacing, "0px")
        self.assertEqual(ctx.fontStretch, "normal")
        self.assertEqual(ctx.fontKerning, "auto")
        self.assertEqual(ctx.fontVariationSettings, "normal")
        self.assertEqual(ctx.fontVariantCaps, "normal")
        # TODO Support textRendering
        # t.is(ctx.textRendering , 'auto')
        # Other properties
        self.assertEqual(ctx.globalCompositeOperation, "source-over")
        self.assertEqual(ctx.imageSmoothingEnabled, True)
        self.assertEqual(ctx.imageSmoothingQuality, "low")
        self.assertEqual(ctx.filter, "none")

        # Verify transform is reset to identity
        transform = ctx.getTransform()
        self.assertEqual(transform.a, 1)
        self.assertEqual(transform.b, 0)
        self.assertEqual(transform.c, 0)
        self.assertEqual(transform.d, 1)
        self.assertEqual(transform.e, 0)
        self.assertEqual(transform.f, 0)

        # Verify state stack is cleared (restore should not change anything)
        ctx.fillStyle = "yellow"
        ctx.restore()
        self.assertEqual(
            ctx.fillStyle, "yellow"
        )  # Should still be yellow, not restored

        # Draw a rect with default styles to verify canvas was cleared
        ctx.fillStyle = "blue"
        ctx.fillRect(200, 200, 100, 100)
        self._snapshot("reset")

    def test_reset_clears_canvas(self):
        ctx = self.ctx
        canvas = self.canvas
        # Fill the entire canvas with red
        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # Reset should clear to transparent
        ctx.reset()

        # Draw something small to verify canvas was cleared
        ctx.fillStyle = "green"
        ctx.fillRect(100, 100, 50, 50)
        self._snapshot("reset-clears-canvas")

    def test_reset_clears_path(self):
        ctx = self.ctx
        # Create a path
        ctx.beginPath()
        ctx.moveTo(50, 50)
        ctx.lineTo(200, 200)
        ctx.lineTo(50, 200)
        ctx.closePath()

        # Reset should clear the path
        ctx.reset()

        # Try to fill the path - nothing should be drawn since path was cleared
        ctx.fillStyle = "red"
        ctx.fill()

        # Draw a small rect to show canvas is working
        ctx.fillStyle = "green"
        ctx.fillRect(100, 100, 50, 50)
        self._snapshot("reset-clears-path")

    def test_reset_clears_clip(self):
        ctx = self.ctx
        canvas = self.canvas
        # Create a clipping region
        ctx.beginPath()
        ctx.rect(100, 100, 100, 100)
        ctx.clip()

        # This rect should be clipped
        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # Reset should clear the clipping region
        ctx.reset()

        # This rect should NOT be clipped
        ctx.fillStyle = "green"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        self._snapshot("reset-clears-clip")

    def test_reset_mdn_example(self):
        ctx = self.ctx

        def drawRect():
            ctx.lineWidth = 10
            ctx.strokeRect(50, 50, 150, 100)
            ctx.font = "50px Iosevka Slab"
            ctx.fillText("Rect", 70, 110)

        def drawCircle():
            ctx.lineWidth = 5
            ctx.beginPath()
            ctx.arc(300, 100, 50, 0, 2 * math.pi)
            ctx.stroke()
            ctx.font = "22px Iosevka Slab"
            ctx.fillText("Circle", 265, 100)

        # Draw rect first
        drawRect()
        # Reset the context (simulates toggle button click)
        ctx.reset()
        # Draw circle after reset
        drawCircle()

        self._snapshot("reset-mdn-example")

    def test_save_restore(self):
        ctx = self.ctx
        # Save the default state
        ctx.save()

        ctx.fillStyle = "green"
        ctx.fillRect(10, 10, 100, 100)

        # Restore the default state
        ctx.restore()

        ctx.fillRect(150, 40, 100, 100)
        self._snapshot("save-restore")

    def test_save_restore_after_layer_promotion(self):
        ctx = self.ctx
        canvas = self.canvas

        # Draw background
        ctx.fillStyle = "lightgray"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # Save state and set up clip
        ctx.save()
        ctx.beginPath()
        ctx.rect(50, 50, 200, 200)
        ctx.clip()

        # Draw inside clip (should be visible)
        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, 300, 300)

        # Trigger layer promotion via getImageData
        ctx.getImageData(0, 0, 1, 1)

        # Draw more inside clip (should still be clipped after layer promotion)
        ctx.fillStyle = "blue"
        ctx.fillRect(100, 100, 200, 200)

        # Restore state - clip should be removed
        ctx.restore()

        # Draw outside the clip area (should be visible since clip was restored)
        ctx.fillStyle = "green"
        ctx.fillRect(300, 50, 150, 200)

        self._snapshot("save-restore-after-layer-promotion")

    def test_save_restore_transform_after_layer_promotion(self):
        ctx = self.ctx
        canvas = self.canvas

        # Draw background
        ctx.fillStyle = "lightgray"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        # Set up initial transform (translate 50, 50)
        ctx.translate(50, 50)

        # Save state with the transform
        ctx.save()

        # Apply additional transform (rotate 45 degrees)
        ctx.rotate(math.pi / 4)

        # Draw rotated red rectangle
        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, 100, 50)

        # Trigger layer promotion via getImageData
        ctx.getImageData(0, 0, 1, 1)

        # Draw more content with current rotated transform
        ctx.fillStyle = "blue"
        ctx.fillRect(0, 60, 100, 50)

        # Restore state - should restore to translate(50, 50) without rotation
        ctx.restore()

        # Draw with restored transform (no rotation, just translate)
        # This rectangle should appear at (50, 200) without rotation
        ctx.fillStyle = "green"
        ctx.fillRect(0, 150, 150, 80)

        self._snapshot("save-restore-transform-after-layer-promotion")

    def test_rotate(self):
        ctx = self.ctx
        # Point of transform origin
        ctx.arc(0, 0, 5, 0, 2 * math.pi)
        ctx.fillStyle = "blue"
        ctx.fill()

        # Non-rotated rectangle
        ctx.fillStyle = "gray"
        ctx.fillRect(100, 0, 80, 20)

        # Rotated rectangle
        ctx.rotate((45 * math.pi) / 180)
        ctx.fillStyle = "red"
        ctx.fillRect(100, 0, 80, 20)
        # Reset transformation matrix to the identity matrix
        ctx.setTransform(1, 0, 0, 1, 0, 0)

        ctx.fillStyle = "hotpink"
        ctx.fillRect(100, 50, 80, 20)
        self._snapshot("rotate")

    def test_scale(self):
        ctx = self.ctx
        # Scaled rectangle
        ctx.scale(9, 3)
        ctx.fillStyle = "red"
        ctx.fillRect(10, 10, 8, 20)

        # Reset current transformation matrix to the identity matrix
        ctx.setTransform(1, 0, 0, 1, 0, 0)

        # Non-scaled rectangle
        ctx.fillStyle = "gray"
        ctx.fillRect(10, 10, 8, 20)
        self._snapshot("scale")

    def test_set_line_dash(self):
        ctx = self.ctx
        # Dashed line
        ctx.beginPath()
        ctx.setLineDash([5, 15])
        ctx.moveTo(0, 50)
        ctx.lineTo(300, 50)
        ctx.stroke()

        # Solid line
        ctx.beginPath()
        ctx.setLineDash([])
        ctx.moveTo(0, 100)
        ctx.lineTo(300, 100)
        ctx.stroke()

        self._snapshot("setLineDash")

    def test_set_transform(self):
        ctx = self.ctx
        ctx.setTransform(1, 0.2, 0.8, 1, 0, 0)
        ctx.fillRect(0, 0, 100, 100)
        self._snapshot("setTransform")

    def test_set_transform_matrix(self):
        ctx = self.ctx
        mat = canvas_pyr.DOMMatrix().rotate(30).skewX(30).scale(1, math.sqrt(3) / 2)
        ctx.setTransform(mat)
        ctx.fillStyle = "red"
        ctx.fillRect(100, 100, 100, 100)
        self._snapshot("setTransform matrix")

    def test_stroke(self):
        ctx = self.ctx
        ctx.lineWidth = 26
        ctx.strokeStyle = "orange"
        ctx.moveTo(20, 20)
        ctx.lineTo(160, 20)
        ctx.stroke()

        ctx.lineWidth = 14
        ctx.strokeStyle = "green"
        ctx.moveTo(20, 80)
        ctx.lineTo(220, 80)
        ctx.stroke()

        ctx.lineWidth = 4
        ctx.strokeStyle = "pink"
        ctx.moveTo(20, 140)
        ctx.lineTo(280, 140)
        ctx.stroke()
        self._snapshot("stroke")

    def test_stroke_and_filling(self):
        ctx = self.ctx
        ctx.lineWidth = 16
        ctx.strokeStyle = "red"

        # Stroke on top of fill
        ctx.beginPath()
        ctx.rect(25, 25, 100, 100)
        ctx.fill()
        ctx.stroke()

        # Fill on top of stroke
        ctx.beginPath()
        ctx.rect(175, 25, 100, 100)
        ctx.stroke()
        ctx.fill()
        self._snapshot("stroke-and-filling")

    def test_stroke_rect(self):
        ctx = self.ctx
        ctx.shadowColor = "#d53"
        ctx.lineJoin = "bevel"
        ctx.lineWidth = 15
        ctx.strokeStyle = "#38f"
        ctx.strokeRect(30, 30, 160, 90)
        self._snapshot("strokeRect")

    def test_stroke_round_rect(self):
        canvas = canvas_pyr.createCanvas(700, 300)
        ctx = canvas.getContext("2d")
        # Rounded rectangle with zero radius (specified as a number)
        ctx.strokeStyle = "red"
        ctx.beginPath()
        ctx.roundRect(10, 20, 150, 100, 0)
        ctx.stroke()

        # Rounded rectangle with 40px radius (single element list)
        ctx.strokeStyle = "blue"
        ctx.beginPath()
        ctx.roundRect(10, 20, 150, 100, [40])
        ctx.stroke()

        # Rounded rectangle with 2 different radii
        ctx.strokeStyle = "orange"
        ctx.beginPath()
        ctx.roundRect(10, 150, 150, 100, [10, 40])
        ctx.stroke()

        # Rounded rectangle with four different radii
        ctx.strokeStyle = "green"
        ctx.beginPath()
        ctx.roundRect(400, 20, 200, 100, [0, 30, 50, 60])
        ctx.stroke()

        # Same rectangle drawn backwards
        ctx.strokeStyle = "magenta"
        ctx.beginPath()
        ctx.roundRect(400, 150, -200, 100, [0, 30, 50, 60])
        ctx.stroke()

        self._snapshot("strokeRoundRect", canvas=canvas)

    def test_stroke_text(self):
        ctx = self.ctx
        canvas = self.canvas
        ctx.fillStyle = "yellow"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.strokeStyle = "black"
        ctx.lineWidth = 3
        ctx.font = "50px Iosevka Slab"
        ctx.strokeText("skr canvas", 50, 150)
        gradient = ctx.createConicGradient(0, 100, 100)

        # Add five color stops
        gradient.addColorStop(0, "red")
        gradient.addColorStop(0.15, "orange")
        gradient.addColorStop(0.25, "yellow")
        gradient.addColorStop(0.35, "orange")
        gradient.addColorStop(0.5, "green")
        gradient.addColorStop(0.75, "cyan")
        gradient.addColorStop(1, "blue")

        # Set the fill style and draw a rectangle
        ctx.strokeStyle = gradient
        ctx.strokeText("@napi-rs/canvas", 50, 300)
        self._snapshot("strokeText", "png", 3.5)

    def test_empty_text(self):
        ctx = self.ctx
        ctx.fillText("", 50, 50)
        ctx.strokeText("", 50, 50)

    @unittest.skip("Not found test emoji font")
    def test_draw_text_emoji(self):
        if sys.platform == "darwin":
            self.skipTest("macOS definitely supports emoji")
            return
        ctx = self.ctx
        canvas_pyr.GlobalFonts.registerFromPath(
            str(self._test_path("fonts", "AppleColorEmoji@2x.ttf"))
        )
        ctx.font = "50px Apple Color Emoji"
        ctx.strokeText("😀😃😄😁😆😅", 50, 100)
        ctx.fillText("😂🤣☺️😊😊😇", 50, 220)
        self._snapshot("draw-text-emoji", "png", 0.05)

    def test_transform(self):
        ctx = self.ctx
        ctx.transform(1, 0.2, 0.8, 1, 0, 0)
        ctx.fillRect(0, 0, 100, 100)
        ctx.resetTransform()
        ctx.fillRect(220, 0, 100, 100)
        self._snapshot("transform")

    def test_translate(self):
        ctx = self.ctx
        drawTranslate(ctx)
        self._snapshot("translate")

    def test_translate_with_transform(self):
        ctx = self.ctx
        ctx.translate(110, 30)
        ctx.transform(1, 0, 0, 1, -20, -10)
        ctx.transform(1, 0, 0, 1, 0, 0)
        ctx.fillStyle = "red"
        ctx.fillRect(-30, -10, 80, 80)
        self._snapshot("translate-with-transform")

    def test_webp_output(self):
        ctx = self.ctx
        drawTranslate(ctx)
        self._snapshot("webp-output", "webp")

    def test_avif_output(self):
        ctx = self.ctx
        drawTranslate(ctx)
        self._snapshot("avif-output", "avif")

    def test_raw_output(self):
        ctx = self.ctx
        canvas = self.canvas
        drawTranslate(ctx)

        output = canvas.data()
        png_from_canvas = canvas.encode("png")
        image = Image.open(BytesIO(png_from_canvas)).convert("RGBA")
        self.assertEqual(output, image.tobytes())

    def test_to_data_url(self):
        ctx = self.ctx
        canvas = self.canvas
        drawTranslate(ctx)

        if not hasattr(canvas, "toDataURL"):
            self.skipTest("canvas.toDataURL not available")
        output = canvas.toDataURL()
        prefix = "data:image/png;base64,"
        self.assertTrue(output.startswith(prefix))
        image_base64 = output[len(prefix) :]
        png_buffer = base64.b64decode(image_base64)
        self.assertEqual(png_buffer, canvas.encode("png"))

    def test_jpeg_to_data_url_with_quality(self):
        ctx = self.ctx
        canvas = self.canvas
        drawTranslate(ctx)

        output = canvas.toDataURL("image/jpeg", 0.2)
        prefix = "data:image/jpeg;base64,"
        self.assertTrue(output.startswith(prefix))
        image_base64 = output[len(prefix) :]
        jpeg_buffer = base64.b64decode(image_base64)
        self.assertEqual(jpeg_buffer, canvas.encode("jpeg", 20))

    def test_webp_to_data_url_with_quality(self):
        ctx = self.ctx
        canvas = self.canvas
        drawTranslate(ctx)

        output = canvas.toDataURL("image/webp", 1)
        prefix = "data:image/webp;base64,"
        self.assertTrue(output.startswith(prefix))
        image_base64 = output[len(prefix) :]
        webp_buffer = base64.b64decode(image_base64)
        self.assertEqual(webp_buffer, canvas.encode("webp", 100))

    def test_shadow_offset_x(self):
        ctx = self.ctx
        ctx.shadowColor = "red"
        ctx.shadowOffsetX = 25
        ctx.shadowBlur = 10

        # Rectangle
        ctx.fillStyle = "blue"
        ctx.fillRect(20, 20, 150, 100)
        self._snapshot("shadowOffsetX")

    def test_should_not_throw_while_fill_stroke_style_invalid(self):
        ctx = self.ctx
        ctx.fillStyle = "#"
        ctx.fillStyle = "#123"
        with self.assertRaises(ValueError):
            ctx.fillStyle = {}  # type: ignore
        ctx.strokeStyle = "#"
        ctx.strokeStyle = "#123"
        with self.assertRaises(ValueError):
            ctx.strokeStyle = {}  # type: ignore

    def test_shadow_offset_y(self):
        ctx = self.ctx
        ctx.shadowColor = "red"
        ctx.shadowOffsetY = 25
        ctx.shadowBlur = 10

        # Rectangle
        ctx.fillStyle = "blue"
        ctx.fillRect(20, 20, 150, 80)
        self._snapshot("shadowOffsetY")

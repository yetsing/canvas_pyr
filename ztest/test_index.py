import base64
import math
import os
import pathlib
import sys
import unittest
from pathlib import Path

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import BaseTestCase, upstream_dir


class IndexTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.canvas = canvas_pyr.createCanvas(1024, 768)
        self.ctx = self.canvas.getContext("2d")

    def test_should_be_able_to_create_path2d(self):
        canvas_pyr.Path2D()
        canvas_pyr.Path2D(
            "M108.956,403.826c0,0,0.178,3.344-1.276,3.311  c-1.455-0.033-30.507-84.917-66.752-80.957C40.928,326.18,72.326,313.197,108.956,403.826z",
        )
        canvas_pyr.Path2D(canvas_pyr.Path2D())

    def test_miter_limit_state(self):
        self.ctx.miterLimit = 10
        self.assertEqual(self.ctx.miterLimit, 10)
        self.ctx.miterLimit = 20
        self.assertEqual(self.ctx.miterLimit, 20)

    def test_global_alpha_state(self):
        self.assertEqual(self.ctx.globalAlpha, 1)
        self.ctx.globalAlpha = 0.2
        self.assertEqual(self.ctx.globalAlpha, 0.2)

    def test_global_composite_operation_state(self):
        self.assertEqual(self.ctx.globalCompositeOperation, "source-over")
        self.ctx.globalCompositeOperation = "xor"
        self.assertEqual(self.ctx.globalCompositeOperation, "xor")

    def test_image_smoothing_enabled_state(self):
        ctx = self.ctx
        self.assertTrue(ctx.imageSmoothingEnabled)
        ctx.imageSmoothingEnabled = False
        self.assertFalse(ctx.imageSmoothingEnabled)

    def test_draw_image_quality_low(self):
        ctx = self.ctx
        ctx.imageSmoothingEnabled = True
        ctx.imageSmoothingQuality = "low"
        self.assertEqual(ctx.imageSmoothingQuality, "low")
        image = self._load_image2("fixtures", "filter-drop-shadow.jpeg")
        ctx.drawImage(image, 0, 0, 426, 322)
        self._snapshot("draw-image-quality-low")

    def test_draw_image_quality_medium(self):
        ctx = self.ctx
        ctx.imageSmoothingEnabled = True
        ctx.imageSmoothingQuality = "medium"
        self.assertEqual(ctx.imageSmoothingQuality, "medium")
        image = self._load_image2("fixtures", "filter-drop-shadow.jpeg")
        ctx.drawImage(image, 0, 0, 426, 322)
        self._snapshot("draw-image-quality-medium")

    def test_draw_image_quality_high(self):
        ctx = self.ctx
        ctx.imageSmoothingEnabled = True
        ctx.imageSmoothingQuality = "high"
        self.assertEqual(ctx.imageSmoothingQuality, "high")
        image = self._load_image2("fixtures", "filter-drop-shadow.jpeg")
        ctx.drawImage(image, 0, 0, 426, 322)
        self._snapshot("draw-image-quality-high")

    def test_line_cap_state(self):
        ctx = self.ctx
        self.assertEqual(ctx.lineCap, "butt")
        ctx.lineCap = "round"
        self.assertEqual(ctx.lineCap, "round")
        ctx.lineCap = "square"
        self.assertEqual(ctx.lineCap, "square")

    def test_line_dash_offset_state(self):
        ctx = self.ctx
        self.assertEqual(ctx.lineDashOffset, 0)
        ctx.lineDashOffset = 10
        self.assertEqual(ctx.lineDashOffset, 10)

    def test_line_join_state(self):
        ctx = self.ctx
        self.assertEqual(ctx.lineJoin, "miter")
        ctx.lineJoin = "round"
        self.assertEqual(ctx.lineJoin, "round")
        ctx.lineJoin = "bevel"
        self.assertEqual(ctx.lineJoin, "bevel")

    def test_line_width_state(self):
        ctx = self.ctx
        self.assertEqual(ctx.lineWidth, 1)
        ctx.lineWidth = 10
        self.assertEqual(ctx.lineWidth, 10)

    def test_fill_style_state(self):
        ctx = self.ctx
        self.assertEqual(ctx.fillStyle, "#000000")
        ctx.fillStyle = "hotpink"
        self.assertEqual(ctx.fillStyle, "hotpink")

    def test_stroke_style_state(self):
        ctx = self.ctx
        self.assertEqual(ctx.strokeStyle, "#000000")
        ctx.strokeStyle = "hotpink"
        self.assertEqual(ctx.strokeStyle, "hotpink")

    def test_shadow_blur_state(self):
        ctx = self.ctx
        self.assertEqual(ctx.shadowBlur, 0)
        ctx.shadowBlur = 10
        self.assertEqual(ctx.shadowBlur, 10)

    def test_shadow_color_state(self):
        ctx = self.ctx
        self.assertEqual(ctx.shadowColor, "#000000")
        ctx.shadowColor = "hotpink"
        self.assertEqual(ctx.shadowColor, "hotpink")

    def test_shadow_offset_x_state(self):
        ctx = self.ctx
        self.assertEqual(ctx.shadowOffsetX, 0)
        ctx.shadowOffsetX = 10
        self.assertEqual(ctx.shadowOffsetX, 10)

    def test_shadow_offset_y_state(self):
        ctx = self.ctx
        self.assertEqual(ctx.shadowOffsetY, 0)
        ctx.shadowOffsetY = 10
        self.assertEqual(ctx.shadowOffsetY, 10)

    def test_line_dash_state(self):
        ctx = self.ctx
        line_dash = [1, 2, 4.5, 7]
        ctx.setLineDash(line_dash)
        self.assertEqual(ctx.getLineDash(), line_dash)

    def test_text_align_state(self):
        ctx = self.ctx
        self.assertEqual(ctx.textAlign, "start")
        ctx.textAlign = "end"
        self.assertEqual(ctx.textAlign, "end")
        ctx.textAlign = "left"
        self.assertEqual(ctx.textAlign, "left")
        ctx.textAlign = "center"
        self.assertEqual(ctx.textAlign, "center")
        ctx.textAlign = "right"
        self.assertEqual(ctx.textAlign, "right")

    def test_text_baseline_state(self):
        ctx = self.ctx
        self.assertEqual(ctx.textBaseline, "alphabetic")
        ctx.textBaseline = "top"
        self.assertEqual(ctx.textBaseline, "top")
        ctx.textBaseline = "hanging"
        self.assertEqual(ctx.textBaseline, "hanging")
        ctx.textBaseline = "middle"
        self.assertEqual(ctx.textBaseline, "middle")
        ctx.textBaseline = "ideographic"
        self.assertEqual(ctx.textBaseline, "ideographic")

    def test_get_transform(self):
        ctx = self.ctx
        transform = ctx.getTransform()
        self.assertEqual(transform, canvas_pyr.DOMMatrix([1, 0, 0, 1, 0, 0]))

    def test_stroke_and_filling_jpeg(self):
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
        self._snapshot("stroke-and-filling-jpeg", "jpeg")

    def test_composition_destination_in(self):
        ctx = self.ctx
        self.canvas.width = 300
        self.canvas.height = 300
        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, 300, 300)
        ctx.save()
        ctx.globalCompositeOperation = "destination-in"
        ctx.fillStyle = "green"
        ctx.beginPath()
        ctx.arc(150, 150, 100, 0, math.pi * 2)
        ctx.closePath()
        ctx.fill()
        ctx.restore()

        self._snapshot("composition-destination-in", "png")

    def test_composition_source_in(self):
        ctx = self.ctx
        self.canvas.width = 300
        self.canvas.height = 300
        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, 300, 300)
        ctx.save()
        ctx.globalCompositeOperation = "source-in"
        ctx.fillStyle = "green"
        ctx.beginPath()
        ctx.arc(150, 150, 100, 0, math.pi * 2)
        ctx.closePath()
        ctx.fill()
        ctx.restore()

        self._snapshot("composition-source-in", "png")

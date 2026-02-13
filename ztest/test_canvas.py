import os
import sys
import unittest
from pathlib import Path

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import DEFAULT_HEIGHT, DEFAULT_WIDTH


class CanvasTestCase(unittest.TestCase):
    """
    Test cases for canvas creation and properties.
    """

    def test_create_canvas(self):
        canvas = canvas_pyr.createCanvas(100, 200)
        self.assertIsNotNone(canvas)
        ctx = canvas.getContext("2d")
        self.assertIsNotNone(ctx)
        self.assertEqual(canvas.width, 100)
        self.assertEqual(canvas.height, 200)

    def test_create_svg_canvas(self):
        flags = [
            canvas_pyr.SvgExportFlag.ConvertTextToPaths,
            canvas_pyr.SvgExportFlag.NoPrettyXML,
            canvas_pyr.SvgExportFlag.RelativePathEncoding,
        ]
        for flag in flags:
            canvas = canvas_pyr.createCanvas(100, 200, flag)
            self.assertIsNotNone(canvas)
            ctx = canvas.getContext("2d")
            self.assertIsNotNone(ctx)
            self.assertEqual(canvas.width, 100)
            self.assertEqual(canvas.height, 200)

    def test_create_canvas_with_non_positive_values(self):
        test_cases = [
            [
                # msg
                "test 1",
                # args
                [0, 0],
                # want width and height
                [DEFAULT_WIDTH, DEFAULT_HEIGHT],
            ],
            [
                "test 2",
                [-1, 10],
                [DEFAULT_WIDTH, 10],
            ],
            [
                "test 3",
                [10, -5],
                [10, DEFAULT_HEIGHT],
            ],
            [
                "test 4",
                [10, -30, canvas_pyr.SvgExportFlag.ConvertTextToPaths],
                [10, DEFAULT_HEIGHT],
            ],
        ]
        for t in test_cases:
            with self.subTest(t[0]):
                _, args, wants = t
                if len(args) == 2:
                    canvas = canvas_pyr.createCanvas(args[0], args[1])
                elif len(args) == 3:
                    canvas = canvas_pyr.createCanvas(args[0], args[1], args[2])
                else:
                    self.fail("Invalid number of arguments in test case")
                self.assertIsNotNone(canvas)
                self.assertEqual(canvas.width, wants[0])
                self.assertEqual(canvas.height, wants[1])

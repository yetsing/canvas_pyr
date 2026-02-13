import sys
from pathlib import Path

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import BaseTestCase


class SimpleTestCase(BaseTestCase):

    def test_non_image_mime_type_with_jpeg_data(self):
        # This is a simple test case using a small PNG image with wrong MIME type
        png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII="

        image = canvas_pyr.Image()
        image.load(f"data:application/octet-stream;base64,{png_base64}")

        self.assertGreater(image.width, 0)
        self.assertGreater(image.height, 0)

    def test_text_mime_type_with_png_data(self):
        # This is a simple test case using a small PNG image with wrong MIME type
        png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII="

        image = canvas_pyr.Image()
        image.load(f"data:text/plain;base64,{png_base64}")

        self.assertGreater(image.width, 0)
        self.assertGreater(image.height, 0)

    def test_correct_image_mime_type(self):
        png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII="

        image = canvas_pyr.Image()
        image.load(f"data:image/png;base64,{png_base64}")

        self.assertGreater(image.width, 0)
        self.assertGreater(image.height, 0)

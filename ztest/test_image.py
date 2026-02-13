import base64
import sys
from pathlib import Path

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import BaseTestCase, upstream_dir


def load_image_file():
    image_path = upstream_dir / "example" / "simple.png"
    return image_path.read_bytes()


def load_fixture_bytes(name: str) -> bytes:
    return (upstream_dir / "__test__" / "fixtures" / name).read_bytes()


def load_fixture_path(name: str) -> str:
    return str(upstream_dir / "__test__" / "fixtures" / name)


class ImageTestCase(BaseTestCase):

    def test_create_image(self):
        canvas_pyr.Image()

    def test_load_image_from_bytes(self):
        image_data = load_image_file()
        img = canvas_pyr.Image()
        img.load(image_data)

    def test_width_and_height_should_be_ok(self):
        image_data = load_image_file()
        img = canvas_pyr.Image()
        img.load(image_data)
        self.assertEqual(img.width, 300)
        self.assertEqual(img.height, 320)
        self.assertEqual(img.naturalWidth, 300)
        self.assertEqual(img.naturalHeight, 320)
        self.assertEqual(img.src, "<bytes>")
        self.assertEqual(img.complete, True)

    def test_alt_state_should_be_ok(self):
        img = canvas_pyr.Image()
        self.assertEqual(img.alt, "")
        img.alt = "hello"
        self.assertEqual(img.alt, "hello")

    def test_with_exif_image_width_and_height_should_be_correct(self):
        image_data = self._test_path("fixtures", "with-exif.jpg").read_bytes()
        img = canvas_pyr.Image()
        img.load(image_data)
        # EXIF rotation is applied during decode, so dimensions are correct after decode()
        self.assertEqual(img.width, 450)
        self.assertEqual(img.height, 600)

    def test_draw_image_exif(self):
        image_data = self._test_path("fixtures", "with-exif.jpg").read_bytes()
        img = canvas_pyr.Image()
        img.load(image_data)
        canvas = canvas_pyr.createCanvas(800, 800)
        ctx = canvas.getContext("2d")
        ctx.drawImage(img, 0, 0)
        self._snapshot("draw-image-exif", canvas=canvas)

    def test_properties_should_be_readonly(self):
        img = canvas_pyr.Image()
        with self.assertRaises(AttributeError):
            img.naturalWidth = 100
        with self.assertRaises(AttributeError):
            img.naturalHeight = 100
        with self.assertRaises(AttributeError):
            img.src = "test.png"
        with self.assertRaises(AttributeError):
            img.complete = False

    def test_svg_transparent_background(self):
        img = canvas_pyr.Image()
        img.load(self._example_path("resize-svg.svg").read_bytes())

        w = 1000
        h = 1000

        # resize SVG
        img.width = w / 2
        img.height = h / 2

        # create a canvas of the same size as the image
        canvas = canvas_pyr.createCanvas(w, h)
        ctx = canvas.getContext("2d")

        # fill the canvas with the image
        ctx.fillStyle = "pink"
        ctx.fillRect(0, 0, w, h)
        ctx.drawImage(img, 250, 250)

        self._snapshot("svg-transparent-background", canvas=canvas)

    def test_reset_src_to_empty_should_not_throw_error(self):
        img = canvas_pyr.Image()
        img.load(b"")
        self.assertEqual(img.complete, True, "complete should be True for empty buffer")

    def test_load_invalid_svg_should_throw_error(self):
        img = canvas_pyr.Image()
        with self.assertRaises(ValueError):
            img.load(b"<svg></svg><p></p>")

    def test_should_be_able_to_load_file_path_as_src(self):
        img = canvas_pyr.Image()
        image_path = self._example_path("simple.png")
        img.load(str(image_path))
        self.assertEqual(img.width, 300)
        self.assertEqual(img.height, 320)
        self.assertEqual(img.naturalWidth, 300)
        self.assertEqual(img.naturalHeight, 320)
        self.assertEqual(img.src, str(image_path))

    def test_should_be_able_to_set_data_url_as_image_src(self):
        img = canvas_pyr.Image()
        image_data = load_image_file()
        data_url = "data:image/png;base64," + base64.b64encode(image_data).decode(
            "ascii"
        )
        img.load(data_url)
        self.assertEqual(img.width, 300)
        self.assertEqual(img.height, 320)
        self.assertEqual(img.naturalWidth, 300)
        self.assertEqual(img.naturalHeight, 320)
        self.assertEqual(img.src, data_url)

    def test_should_throw_error_for_invalid_data_url(self):
        img = canvas_pyr.Image()
        with self.assertRaises(ValueError):
            img.load("data:image/png;base64,invalid")

    def test_complete_should_be_true_initially(self):
        img = canvas_pyr.Image()
        self.assertEqual(
            img.complete, True, "complete should be true when no src is set"
        )

    def test_current_src_should_be_null_initially(self):
        img = canvas_pyr.Image()
        self.assertIsNone(img.currentSrc, "currentSrc should be null initially")

    def test_current_src_after_load(self):
        img = canvas_pyr.Image()
        self.assertIsNone(img.currentSrc, "currentSrc should be null initially")
        image_data = load_image_file()
        img.load(image_data)
        self.assertEqual(
            img.currentSrc,
            "<bytes>",
            "currentSrc should be '<bytes>' after loading from bytes",
        )

    def test_current_src_after_load_file_path(self):
        img = canvas_pyr.Image()
        self.assertIsNone(img.currentSrc, "currentSrc should be null initially")
        image_path = self._example_path("simple.png")
        img.load(str(image_path))
        self.assertEqual(
            img.currentSrc,
            str(image_path),
            "currentSrc should be the file path after loading from file path",
        )

    def test_clearing_src_should_reset_properties(self):
        img = canvas_pyr.Image()
        image_data = load_image_file()
        img.load(image_data)
        self.assertEqual(img.width, 300)
        self.assertEqual(img.height, 320)
        self.assertEqual(img.naturalWidth, 300)
        self.assertEqual(img.naturalHeight, 320)
        self.assertEqual(img.src, "<bytes>")
        self.assertEqual(img.currentSrc, "<bytes>")
        self.assertEqual(img.complete, True)

        # Clear the src by loading an empty buffer
        img.load(b"")
        self.assertEqual(img.width, 0)
        self.assertEqual(img.height, 0)
        self.assertEqual(img.naturalWidth, 0)
        self.assertEqual(img.naturalHeight, 0)
        self.assertIsNone(img.src)
        self.assertIsNone(img.currentSrc)
        self.assertEqual(img.complete, True)

    def test_current_src_should_not_change_on_failed_load(self):
        img = canvas_pyr.Image()
        image_data = load_image_file()
        img.load(image_data)
        self.assertEqual(
            img.currentSrc,
            "<bytes>",
            "currentSrc should be '<bytes>' after loading from bytes",
        )

        # Attempt to load invalid data
        with self.assertRaises(ValueError):
            img.load("data:image/png;base64,invalid")

        # currentSrc should remain unchanged
        self.assertEqual(
            img.currentSrc,
            "<bytes>",
            "currentSrc should remain '<bytes>' after failed load",
        )

    def test_small_buffers_should_be_treated_as_empty(self):
        img = canvas_pyr.Image()
        for buffer in [b"", b"\0", b"\0\1", b"\0\1\2", b"\0\1\2\3"]:
            img.load(buffer)
            self.assertEqual(img.width, 0)
            self.assertEqual(img.height, 0)
            self.assertEqual(img.naturalWidth, 0)
            self.assertEqual(img.naturalHeight, 0)
            self.assertIsNone(img.src)
            self.assertIsNone(img.currentSrc)
            self.assertEqual(img.complete, True)

    def test_complete_should_be_true_after_file_read_errors(self):
        img = canvas_pyr.Image()
        # Attempt to load a non-existent file
        with self.assertRaises(RuntimeError):
            img.load("/non_existent_file.png")
        self.assertEqual(
            img.complete, True, "complete should be true after file read error"
        )

    def test_complete_should_be_true_after_base64_decode_errors(self):
        img = canvas_pyr.Image()
        # Attempt to load an invalid data URL
        with self.assertRaises(ValueError):
            img.load("data:image/png;base64,invalid_base64")
        self.assertEqual(
            img.complete, True, "complete should be true after base64 decode error"
        )

    def test_overlapping_loads(self):
        img = canvas_pyr.Image()
        filepath1 = self._example_path("simple.png")
        filepath2 = self._test_path("fixtures", "with-exif.jpg")

        img.load(str(filepath1))
        img.load(str(filepath2))

        self.assertTrue(img.complete)
        self.assertEqual(img.naturalWidth, 450)
        self.assertEqual(img.naturalHeight, 600)

    def test_failed_svg_load_should_clear_state(self):
        img = canvas_pyr.Image()
        img.load(load_image_file())

        self.assertEqual(img.width, 300)
        self.assertEqual(img.height, 320)
        self.assertEqual(img.naturalWidth, 300)
        self.assertEqual(img.naturalHeight, 320)
        self.assertTrue(img.complete)

        with self.assertRaises(ValueError):
            img.load(b"<svg><")  # Malformed XML

        self.assertEqual(img.width, 0)
        self.assertEqual(img.height, 0)
        self.assertEqual(img.naturalWidth, 0)
        self.assertEqual(img.naturalHeight, 0)
        self.assertTrue(img.complete)

        canvas = canvas_pyr.createCanvas(100, 100)
        ctx = canvas.getContext("2d")
        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, 100, 100)
        ctx.drawImage(img, 0, 0)

        image_data = ctx.getImageData(50, 50, 1, 1)
        self.assertEqual(image_data.data[0], 255)  # Red channel should be 255
        self.assertEqual(image_data.data[1], 0)  # Green channel should be 0
        self.assertEqual(image_data.data[2], 0)  # Blue channel should be 0
        self.assertEqual(
            image_data.data[3], 255
        )  # Alpha channel should be 255 (opaque)

    def test_avif_from_buffer_should_work(self):
        img = canvas_pyr.Image()
        avif_path = self._test_path("fixtures", "issue-996.avif")
        img.load(avif_path.read_bytes())

        # Verify image loaded successfully
        self.assertTrue(img.complete)
        self.assertGreater(img.naturalWidth, 0)
        self.assertGreater(img.naturalHeight, 0)

        # Verify we can draw it - check that bitmap exists and drawImage doesn't throw
        canvas = canvas_pyr.createCanvas(int(img.width), int(img.height))
        ctx = canvas.getContext("2d")
        ctx.drawImage(img, 0, 0)

        # Verify pixels were drawn by checking that at least some pixels have content.
        # We check for any non-zero RGBA values to handle both opaque and semi-transparent images.
        # Note: This test assumes the issue-996.avif fixture has visible content (not fully transparent).
        image_data = ctx.getImageData(0, 0, canvas.width, canvas.height)
        has_visible_pixel = False
        for i in range(0, len(image_data.data), 4):
            r, g, b, a = image_data.data[i : i + 4]
            if r != 0 or g != 0 or b != 0 or a != 0:
                has_visible_pixel = True
                break
        self.assertTrue(
            has_visible_pixel, "AVIF image should have been drawn (has visible pixels)"
        )

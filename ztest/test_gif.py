import base64
import math
import pathlib
import unittest

import canvas_pyr

script_dir = pathlib.Path(__file__).resolve().parent

# GIF magic bytes: GIF87a or GIF89a
GIF_MAGIC = bytes([0x47, 0x49, 0x46, 0x38])  # "GIF8"


def is_valid_gif(data: bytes) -> bool:
    return data.startswith(GIF_MAGIC)


class GifTestCase(unittest.TestCase):
    def test_encode_single_frame_gif(self):
        canvas = canvas_pyr.createCanvas(100, 100)
        ctx = canvas.getContext("2d")

        ctx.fillStyle = "red"
        ctx.fillRect(0, 0, 100, 100)

        gif_data = canvas.encode("gif")
        self.assertTrue(is_valid_gif(gif_data))

    def test_encode_single_frame_gif_with_quality_option(self):
        canvas = canvas_pyr.createCanvas(100, 100)
        ctx = canvas.getContext("2d")

        ctx.fillStyle = "blue"
        ctx.fillRect(0, 0, 100, 100)

        gif_data_low_quality = canvas.encode("gif", 30)
        gif_data_high_quality = canvas.encode("gif", 1)

        self.assertTrue(is_valid_gif(gif_data_low_quality))
        self.assertTrue(is_valid_gif(gif_data_high_quality))

    def test_to_data_url_with_gif_mime_type(self):
        canvas = canvas_pyr.createCanvas(50, 50)
        ctx = canvas.getContext("2d")

        ctx.fillStyle = "green"
        ctx.fillRect(0, 0, 50, 50)

        data_url = canvas.toDataURL("image/gif")
        self.assertTrue(data_url.startswith("data:image/gif;base64,"))

        # Decode and verify it's a valid GIF
        base64_data = data_url.split(",")[1]
        gif_data = base64.b64decode(base64_data)
        self.assertTrue(is_valid_gif(gif_data))


class GifEncoderTestCase(unittest.TestCase):

    def test_constructor(self):
        encoder = canvas_pyr.GifEncoder(100, 100)
        self.assertIsInstance(encoder, canvas_pyr.GifEncoder)
        self.assertEqual(encoder.width, 100)
        self.assertEqual(encoder.height, 100)
        self.assertEqual(encoder.frameCount, 0)

    def test_with_config_options(self):
        encoder = canvas_pyr.GifEncoder(200, 150, {"repeat": 0, "quality": 10})
        self.assertIsInstance(encoder, canvas_pyr.GifEncoder)
        self.assertEqual(encoder.width, 200)
        self.assertEqual(encoder.height, 150)
        self.assertEqual(encoder.frameCount, 0)

    def test_add_frame_with_rgba_data(self):
        encoder = canvas_pyr.GifEncoder(10, 10)

        data = bytearray(10 * 10 * 4)
        for i in range(10 * 10):
            data[i * 4 + 0] = 255  # Red
            data[i * 4 + 1] = 0  # Green
            data[i * 4 + 2] = 0  # Blue
            data[i * 4 + 3] = 255  # Alpha

        encoder.addFrame(data, 10, 10, {"delay": 100})
        self.assertEqual(encoder.frameCount, 1)

    def test_finish_produces_valid_gif(self):
        encoder = canvas_pyr.GifEncoder(10, 10)

        data = bytearray(10 * 10 * 4)
        for i in range(10 * 10):
            data[i * 4 + 0] = 255  # Red
            data[i * 4 + 1] = 0  # Green
            data[i * 4 + 2] = 0  # Blue
            data[i * 4 + 3] = 255  # Alpha

        encoder.addFrame(data, 10, 10, {"delay": 100})

        gif_data = encoder.finish()
        self.assertTrue(is_valid_gif(gif_data))

    def test_creates_animated_gif_with_multiple_frames(self):
        encoder = canvas_pyr.GifEncoder(10, 10, {"repeat": 0})

        red = bytearray(10 * 10 * 4)
        blue = bytearray(10 * 10 * 4)
        green = bytearray(10 * 10 * 4)
        for i in range(10 * 10):
            red[i * 4 + 0] = 255
            red[i * 4 + 3] = 255
            blue[i * 4 + 2] = 255
            blue[i * 4 + 3] = 255
            green[i * 4 + 1] = 255
            green[i * 4 + 3] = 255

        encoder.addFrame(red, 10, 10, {"delay": 500})
        encoder.addFrame(blue, 10, 10, {"delay": 500})
        encoder.addFrame(green, 10, 10, {"delay": 500})

        self.assertEqual(encoder.frameCount, 3)
        gif_data = encoder.finish()
        self.assertTrue(is_valid_gif(gif_data))
        # Animated GIF should be larger than single frame
        self.assertTrue(len(gif_data) > 100)

    def test_with_disposal_methods(self):
        encoder = canvas_pyr.GifEncoder(10, 10, {"repeat": 0})
        frame = bytearray(10 * 10 * 4)
        for i in range(10 * 10):
            frame[i * 4 + 0] = 255
            frame[i * 4 + 3] = 255

        encoder.addFrame(
            frame, 10, 10, {"delay": 100, "disposal": canvas_pyr.GifDisposal.Keep}
        )
        encoder.addFrame(
            frame, 10, 10, {"delay": 100, "disposal": canvas_pyr.GifDisposal.Background}
        )
        encoder.addFrame(
            frame, 10, 10, {"delay": 100, "disposal": canvas_pyr.GifDisposal.Previous}
        )

        gif_data = encoder.finish()
        self.assertTrue(is_valid_gif(gif_data))

    def test_with_frame_offset(self):
        encoder = canvas_pyr.GifEncoder(20, 20, {"repeat": 0})
        frame = bytearray(5 * 5 * 4)
        for i in range(5 * 5):
            frame[i * 4 + 0] = 255
            frame[i * 4 + 3] = 255

        encoder.addFrame(frame, 5, 5, {"delay": 100, "left": 0, "top": 0})
        encoder.addFrame(frame, 5, 5, {"delay": 100, "left": 5, "top": 5})
        encoder.addFrame(frame, 5, 5, {"delay": 100, "left": 10, "top": 10})

        gif_data = encoder.finish()
        self.assertTrue(is_valid_gif(gif_data))

    def test_throws_error_with_no_frames(self):
        encoder = canvas_pyr.GifEncoder(10, 10)
        with self.assertRaises(Exception):
            encoder.finish()

    def test_throws_error_with_invalid_data_length(self):
        encoder = canvas_pyr.GifEncoder(10, 10)
        wrong = bytearray(100)
        with self.assertRaises(Exception):
            encoder.addFrame(wrong, 10, 10)

    def test_clears_frames_after_finish(self):
        encoder = canvas_pyr.GifEncoder(10, 10)
        frame = bytearray(10 * 10 * 4)
        for i in range(10 * 10):
            frame[i * 4 + 0] = 255
            frame[i * 4 + 3] = 255

        encoder.addFrame(frame, 10, 10, {"delay": 100})
        self.assertEqual(encoder.frameCount, 1)

        encoder.finish()
        self.assertEqual(encoder.frameCount, 0)

    def test_gif_encoder_with_finite_repeat_count(self):
        encoder = canvas_pyr.GifEncoder(10, 10, {"repeat": 3})
        frame = bytearray(10 * 10 * 4)
        for i in range(10 * 10):
            frame[i * 4 + 0] = 128
            frame[i * 4 + 1] = 128
            frame[i * 4 + 2] = 128
            frame[i * 4 + 3] = 255

        encoder.addFrame(frame, 10, 10, {"delay": 100})
        encoder.addFrame(frame, 10, 10, {"delay": 100})
        gif_data = encoder.finish()
        self.assertTrue(is_valid_gif(gif_data))

    def test_with_canvas_drawn_frames(self):
        width, height = 50, 50
        encoder = canvas_pyr.GifEncoder(width, height, {"repeat": 0, "quality": 10})
        canvas = canvas_pyr.createCanvas(width, height)
        ctx = canvas.getContext("2d")

        # Frame 1: Red circle
        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, width, height)
        ctx.fillStyle = "red"
        ctx.beginPath()
        ctx.arc(25, 25, 20, 0, math.pi * 2)
        ctx.fill()

        image_data = ctx.getImageData(0, 0, width, height)
        encoder.addFrame(image_data.data, width, height, {"delay": 200})

        # Frame 2: Blue circle
        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, width, height)
        ctx.fillStyle = "blue"
        ctx.beginPath()
        ctx.arc(25, 25, 20, 0, math.pi * 2)
        ctx.fill()

        image_data = ctx.getImageData(0, 0, width, height)
        encoder.addFrame(image_data.data, width, height, {"delay": 200})

        # Frame 3: Green circle
        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, width, height)
        ctx.fillStyle = "green"
        ctx.beginPath()
        ctx.arc(25, 25, 20, 0, math.pi * 2)
        ctx.fill()

        image_data = ctx.getImageData(0, 0, width, height)
        encoder.addFrame(image_data.data, width, height, {"delay": 200})

        self.assertEqual(encoder.frameCount, 3)
        gif_data = encoder.finish()
        self.assertTrue(is_valid_gif(gif_data))
        self.assertTrue(len(gif_data) > 500)  # Should be reasonably sized

    def test_with_transparency(self):
        encoder = canvas_pyr.GifEncoder(10, 10, {"repeat": 0})

        # Frame with semi-transparent pixels
        frame = bytearray(10 * 10 * 4)
        for i in range(10 * 10):
            frame[i * 4 + 0] = 255
            frame[i * 4 + 3] = 0 if i < 50 else 255

        encoder.addFrame(frame, 10, 10, {"delay": 100})
        gif_data = encoder.finish()
        self.assertTrue(is_valid_gif(gif_data))

    def test_encode_gif_with_gradient(self):
        canvas = canvas_pyr.createCanvas(100, 100)
        ctx = canvas.getContext("2d")

        # Create a gradient with many colors
        gradient = ctx.createLinearGradient(0, 0, 100, 100)
        gradient.addColorStop(0, "red")
        gradient.addColorStop(0.25, "yellow")
        gradient.addColorStop(0.5, "green")
        gradient.addColorStop(0.75, "blue")
        gradient.addColorStop(1, "purple")

        ctx.fillStyle = gradient
        ctx.fillRect(0, 0, 100, 100)

        # GIF can only have 256 colors, so this tests the color quantization
        gif_data = canvas.encode("gif", 10)
        self.assertTrue(is_valid_gif(gif_data))
        self.assertGreater(len(gif_data), 0)

    def test_dispose_clears_frames(self):
        if not hasattr(canvas_pyr.GifEncoder(1, 1), "dispose"):
            self.skipTest("dispose not available in this binding")
        with canvas_pyr.GifEncoder(10, 10) as encoder:
            frame = bytearray(10 * 10 * 4)
            for i in range(10 * 10):
                frame[i * 4 + 0] = 255
                frame[i * 4 + 3] = 255

            encoder.addFrame(frame, 10, 10, {"delay": 100})
            self.assertEqual(encoder.frameCount, 1)
        self.assertEqual(encoder.frameCount, 0)

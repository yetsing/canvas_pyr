import sys
from array import array
from pathlib import Path

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import BaseTestCase


class ImageDataTestCase(BaseTestCase):
    def test_should_be_able_to_create_image_data(self):
        self.assertIsNotNone(canvas_pyr.ImageData(1024, 768))

    def test_should_be_able_to_create_from_uint8(self):
        pixel_array = array("B", [255] * (4 * 4 * 4))
        image_data = canvas_pyr.ImageData(pixel_array.tobytes(), 4, 4)
        self.assertEqual(image_data.width, 4)
        self.assertEqual(image_data.height, 4)
        self.assertEqual(list(image_data.data), list(pixel_array))

    def test_should_be_able_to_create_from_uint8_without_height(self):
        pixel_array = array("B", [233] * (4 * 4 * 4))
        image_data = canvas_pyr.ImageData(pixel_array.tobytes(), 4)
        self.assertEqual(image_data.width, 4)
        self.assertEqual(image_data.height, 4)
        self.assertEqual(list(image_data.data), list(pixel_array))

    def test_should_throw_if_size_mismatch(self):
        pixel_array = array("B", [255] * (4 * 4 * 4))
        with self.assertRaisesRegex(
            ValueError, "Index or size is negative or greater than the allowed amount"
        ):
            canvas_pyr.ImageData(pixel_array.tobytes(), 4, 3)

    def test_properties_should_be_readonly(self):
        image_data = canvas_pyr.ImageData(1024, 768)
        fake_data = array("B")
        with self.assertRaises((TypeError, AttributeError)):
            image_data.data = fake_data  # type: ignore
        with self.assertRaises((TypeError, AttributeError)):
            image_data.width = 114
        with self.assertRaises((TypeError, AttributeError)):
            image_data.height = 514

    def test_should_be_able_to_create_from_uint16(self):
        pixel_array = array("H", [65535] * (2 * 2 * 4))
        image_data = canvas_pyr.ImageData(list(pixel_array), 2, 2)
        self.assertEqual(image_data.width, 2)
        self.assertEqual(image_data.height, 2)
        self.assertEqual(len(image_data.data), 16)
        self.assertEqual(list(image_data.data)[0], 255)

    def test_should_be_able_to_create_from_uint16_without_height(self):
        pixel_array = array("H", [32768] * (2 * 2 * 4))
        image_data = canvas_pyr.ImageData(list(pixel_array), 2)
        self.assertEqual(image_data.width, 2)
        self.assertEqual(image_data.height, 2)
        first = list(image_data.data)[0]
        self.assertTrue(127 <= first <= 129)

    def test_should_be_able_to_create_from_float32(self):
        pixel_array = array("f", [1.0] * (2 * 2 * 4))
        image_data = canvas_pyr.ImageData(list(pixel_array), 2, 2)
        self.assertEqual(image_data.width, 2)
        self.assertEqual(image_data.height, 2)
        self.assertEqual(len(image_data.data), 16)
        self.assertEqual(list(image_data.data)[0], 255)

    def test_should_be_able_to_create_from_float32_without_height(self):
        pixel_array = array("f", [0.5] * (2 * 2 * 4))
        image_data = canvas_pyr.ImageData(list(pixel_array), 2)
        self.assertEqual(image_data.width, 2)
        self.assertEqual(image_data.height, 2)
        first = list(image_data.data)[0]
        self.assertTrue(127 <= first <= 128)

    def test_should_clamp_float32_values(self):
        pixel_array = array(
            "f",
            [
                -0.5,
                0.0,
                0.5,
                1.0,
                1.5,
                2.0,
                0.25,
                0.75,
                -1.0,
                0.1,
                0.9,
                1.1,
                0.0,
                0.5,
                1.0,
                2.0,
            ],
        )
        image_data = canvas_pyr.ImageData(list(pixel_array), 2, 2)
        data = list(image_data.data)
        self.assertEqual(image_data.width, 2)
        self.assertEqual(image_data.height, 2)
        self.assertEqual(data[0], 0)
        self.assertEqual(data[1], 0)
        self.assertTrue(127 <= data[2] <= 128)
        self.assertEqual(data[3], 255)
        self.assertEqual(data[4], 255)
        self.assertEqual(data[5], 255)

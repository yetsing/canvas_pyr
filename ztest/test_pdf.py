import math
import sys
from pathlib import Path

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import BaseTestCase


class PDFTestCase(BaseTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.doc = canvas_pyr.PDFDocument()

    def test_create_simple_pdf(self):
        doc = self.doc
        ctx = doc.beginPage(612, 792)  # Letter size in points

        ctx.fillStyle = "blue"
        ctx.fillRect(50, 50, 200, 200)

        doc.endPage()
        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)
        self.assertTrue(pdf_data.startswith(b"%PDF-"))

    def test_create_pdf_with_metadata(self):
        doc = canvas_pyr.PDFDocument(
            {
                "title": "Test Document",
                "author": "Test Author",
                "subject": "Test Subject",
                "keywords": "test, pdf, canvas",
                "creator": "Test Creator",
            }
        )

        ctx = doc.beginPage(612, 792)
        ctx.fillStyle = "red"
        ctx.fillRect(100, 100, 100, 100)
        doc.endPage()

        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)
        self.assertTrue(pdf_data.startswith(b"%PDF-"))

        # Check if metadata is present in the PDF
        pdf_content = pdf_data.decode("latin1")
        self.assertIn("Test Document", pdf_content)
        self.assertIn("Test Author", pdf_content)

    def test_create_pdf_with_multiple_pages(self):
        doc = self.doc

        # Page 1
        ctx1 = doc.beginPage(612, 792)
        ctx1.fillStyle = "red"
        ctx1.fillRect(50, 50, 100, 100)
        ctx1.font = "24px sans-serif"
        ctx1.fillText("Page 1", 50, 200)
        doc.endPage()

        # Page 2
        ctx2 = doc.beginPage(612, 792)
        ctx2.fillStyle = "blue"
        ctx2.fillRect(50, 50, 100, 100)
        ctx2.font = "24px sans-serif"
        ctx2.fillText("Page 2", 50, 200)
        doc.endPage()

        # Page 3
        ctx3 = doc.beginPage(612, 792)
        ctx3.fillStyle = "green"
        ctx3.fillRect(50, 50, 100, 100)
        ctx3.font = "24px sans-serif"
        ctx3.fillText("Page 3", 50, 200)
        doc.endPage()

        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)
        self.assertTrue(pdf_data.startswith(b"%PDF-"))

        # Check for multiple pages - PDF should contain page references
        pdf_content = pdf_data.decode("latin1")
        self.assertIn("/Type /Page", pdf_content)

    def test_draw_various_shapes_on_pdf(self):
        doc = self.doc
        ctx = doc.beginPage(800, 600)

        # Background
        ctx.fillStyle = "white"
        ctx.fillRect(0, 0, 800, 600)

        # Rectangle
        ctx.fillStyle = "red"
        ctx.fillRect(50, 50, 100, 100)

        # Stroked rectangle
        ctx.strokeStyle = "blue"
        ctx.lineWidth = 5
        ctx.strokeRect(200, 50, 100, 100)

        # Circle
        ctx.fillStyle = "green"
        ctx.beginPath()
        ctx.arc(400, 100, 50, 0, math.pi * 2)
        ctx.fill()

        # Line
        ctx.strokeStyle = "purple"
        ctx.lineWidth = 3
        ctx.beginPath()
        ctx.moveTo(50, 250)
        ctx.lineTo(350, 250)
        ctx.stroke()

        # Path with bezier curves
        ctx.strokeStyle = "orange"
        ctx.lineWidth = 2
        ctx.beginPath()
        ctx.moveTo(50, 350)
        ctx.bezierCurveTo(150, 300, 250, 400, 350, 350)
        ctx.stroke()

        doc.endPage()
        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)
        self.assertTrue(pdf_data.startswith(b"%PDF-"))

    def test_render_text_on_pdf(self):
        fond_path = self._test_path("fonts-dir", "iosevka-curly-regular.woff2")
        canvas_pyr.GlobalFonts.registerFromPath(str(fond_path), "i-curly")
        doc = self.doc
        ctx = doc.beginPage(612, 792)

        ctx.fillStyle = "black"
        ctx.font = "24px sans-serif"
        ctx.fillText("Hello PDF World!", 50, 100)

        ctx.font = "36px i-curly"
        ctx.fillStyle = "blue"
        ctx.fillText("@napi-rs/canvas", 50, 200)

        ctx.strokeStyle = "red"
        ctx.lineWidth = 1
        ctx.font = "48px sans-serif"
        ctx.strokeText("Stroked Text", 50, 300)

        doc.endPage()
        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)
        self.assertTrue(pdf_data.startswith(b"%PDF-"))

        self._test_path("pdf", "text.pdf").write_bytes(pdf_data)

    def test_support_gradients_on_pdf(self):
        doc = self.doc
        ctx = doc.beginPage(400, 400)

        # Linear gradient
        linearGradient = ctx.createLinearGradient(0, 0, 200, 0)
        linearGradient.addColorStop(0, "red")
        linearGradient.addColorStop(0.5, "yellow")
        linearGradient.addColorStop(1, "green")
        ctx.fillStyle = linearGradient
        ctx.fillRect(50, 50, 200, 100)

        # Radial gradient
        radialGradient = ctx.createRadialGradient(150, 250, 10, 150, 250, 80)
        radialGradient.addColorStop(0, "white")
        radialGradient.addColorStop(1, "blue")
        ctx.fillStyle = radialGradient
        ctx.fillRect(50, 200, 200, 150)

        doc.endPage()
        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)
        self.assertTrue(pdf_data.startswith(b"%PDF-"))

        self._test_path("pdf", "gradients.pdf").write_bytes(pdf_data)

    def test_support_different_page_sizes(self):
        doc = self.doc

        # A4 size (210mm x 297mm = 595pt x 842pt)
        ctx1 = doc.beginPage(595, 842)
        ctx1.fillStyle = "lightblue"
        ctx1.fillRect(0, 0, 595, 842)
        ctx1.fillStyle = "black"
        ctx1.font = "20px sans-serif"
        ctx1.fillText("A4 Page", 50, 50)
        doc.endPage()

        # Letter size (8.5in x 11in = 612pt x 792pt)
        ctx2 = doc.beginPage(612, 792)
        ctx2.fillStyle = "lightgreen"
        ctx2.fillRect(0, 0, 612, 792)
        ctx2.fillStyle = "black"
        ctx2.font = "20px sans-serif"
        ctx2.fillText("Letter Page", 50, 50)
        doc.endPage()

        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)
        self.assertTrue(pdf_data.startswith(b"%PDF-"))

        self._test_path("pdf", "multi-page.pdf").write_bytes(pdf_data)

    def test_support_pdf_a_and_compression_settings(self):
        doc = canvas_pyr.PDFDocument(
            {
                "title": "Compressed PDF",
                "pdfa": True,
                "compressionLevel": 9,  # High compression
                "encodingQuality": 85,
            }
        )

        ctx = doc.beginPage(612, 792)
        ctx.fillStyle = "red"
        ctx.fillRect(50, 50, 200, 200)
        doc.endPage()

        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)
        self.assertTrue(pdf_data.startswith(b"%PDF-"))

    def test_handle_empty_pdf_document(self):
        doc = self.doc
        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertEqual(len(pdf_data), 0)

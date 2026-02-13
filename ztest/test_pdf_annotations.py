import math
import sys
from pathlib import Path

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import BaseTestCase


class PDFAnnotationTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.doc = canvas_pyr.PDFDocument()

    def test_create_pdf_with_url_link_annotation(self):
        doc = self.doc
        ctx = doc.beginPage(612, 792)

        # Draw a clickable link
        ctx.fillStyle = "blue"
        ctx.fillRect(50, 50, 200, 40)
        ctx.fillStyle = "white"
        ctx.font = "20px sans-serif"
        ctx.fillText("Click here to visit GitHub", 60, 75)

        # Add URL annotation
        ctx.annotateLinkUrl(50, 50, 250, 90, "https://github.com/Brooooooklyn/canvas")

        doc.endPage()
        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)
        self.assertTrue(pdf_data.startswith(b"%PDF-"))

        # Check for annotation in PDF content
        pdf_content = pdf_data.decode("latin1")
        self.assertIn("/Annot", pdf_content)

        self._test_path("pdf", "link-annotation.pdf").write_bytes(pdf_data)

    def test_create_pdf_with_named_destination(self):
        doc = self.doc

        # Page 1 - Create link to destination
        ctx1 = doc.beginPage(612, 792)
        ctx1.fillStyle = "black"
        ctx1.font = "24px sans-serif"
        ctx1.fillText("Table of Contents", 50, 50)

        # Draw a clickable link to page 2
        ctx1.fillStyle = "blue"
        ctx1.fillRect(50, 100, 200, 30)
        ctx1.fillStyle = "white"
        ctx1.font = "18px sans-serif"
        ctx1.fillText("Go to Chapter 1", 60, 120)

        # Add link to named destination
        ctx1.annotateLinkToDestination(50, 100, 250, 130, "chapter1")

        doc.endPage()

        # Page 2 - Create the destination
        ctx2 = doc.beginPage(612, 792)

        # Create named destination at the top of page 2
        ctx2.annotateNamedDestination(50, 50, "chapter1")

        ctx2.fillStyle = "black"
        ctx2.font = "30px sans-serif"
        ctx2.fillText("Chapter 1", 50, 100)
        ctx2.font = "16px sans-serif"
        ctx2.fillText("This is the content of chapter 1.", 50, 150)

        doc.endPage()

        pdf_buffer = doc.close()

        self.assertIsInstance(pdf_buffer, bytes)
        self.assertGreater(len(pdf_buffer), 0)
        self.assertTrue(pdf_buffer.startswith(b"%PDF-"))

        self._test_path("pdf", "named-destination.pdf").write_bytes(pdf_buffer)

    def test_create_pdf_with_multiple_url_links(self):
        doc = self.doc
        ctx = doc.beginPage(612, 792)

        ctx.fillStyle = "black"
        ctx.font = "24px sans-serif"
        ctx.fillText("Useful Links", 50, 50)

        links = [
            {
                "text": "GitHub Repository",
                "url": "https://github.com/Brooooooklyn/canvas",
                "y": 100,
            },
            {
                "text": "NPM Package",
                "url": "https://www.npmjs.com/package/@napi-rs/canvas",
                "y": 160,
            },
            {
                "text": "Documentation",
                "url": "https://github.com/Brooooooklyn/canvas#readme",
                "y": 220,
            },
        ]

        for link in links:
            # Draw link background
            ctx.fillStyle = "lightblue"
            ctx.fillRect(50, link["y"], 300, 40)

            # Draw link text
            ctx.fillStyle = "darkblue"
            ctx.font = "18px sans-serif"
            ctx.fillText(link["text"], 60, link["y"] + 25)

            # Add URL annotation
            ctx.annotateLinkUrl(50, link["y"], 350, link["y"] + 40, link["url"])

        doc.endPage()
        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)
        self.assertTrue(pdf_data.startswith(b"%PDF-"))

        self._test_path("pdf", "multiple-links.pdf").write_bytes(pdf_data)

    def test_create_table_of_contents_with_multiple_named_destinations(self):
        doc = self.doc

        # Table of Contents page
        toc = doc.beginPage(612, 792)
        toc.fillStyle = "black"
        toc.font = "30px sans-serif"
        toc.fillText("Table of Contents", 50, 50)

        chapters = [
            {"title": "Chapter 1: Introduction", "dest": "intro", "y": 120},
            {
                "title": "Chapter 2: Getting Started",
                "dest": "getting-started",
                "y": 160,
            },
            {"title": "Chapter 3: Advanced Topics", "dest": "advanced", "y": 200},
            {"title": "Chapter 4: Conclusion", "dest": "conclusion", "y": 240},
        ]

        toc.font = "18px sans-serif"
        for chapter in chapters:
            toc.fillStyle = "blue"
            toc.fillText(chapter["title"], 70, chapter["y"])
            toc.annotateLinkToDestination(
                70, chapter["y"] - 20, 400, chapter["y"] + 5, chapter["dest"]
            )

        doc.endPage()

        # Create pages for each chapter
        for chapter in chapters:
            ctx = doc.beginPage(612, 792)
            ctx.annotateNamedDestination(50, 50, chapter["dest"])
            ctx.fillStyle = "black"
            ctx.font = "30px sans-serif"
            ctx.fillText(chapter["title"].split(":")[0], 50, 100)
            ctx.font = "18px sans-serif"
            ctx.fillText(f'Content of {chapter["title"].lower()}.', 50, 150)
            doc.endPage()

        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)
        self.assertTrue(pdf_data.startswith(b"%PDF-"))

        self._test_path("pdf", "toc-with-destinations.pdf").write_bytes(pdf_data)

    def test_handle_empty_string_url_gracefully(self):
        doc = self.doc
        ctx = doc.beginPage(612, 792)

        ctx.fillStyle = "black"
        ctx.fillRect(50, 50, 100, 100)

        # Should not crash with empty URL
        ctx.annotateLinkUrl(50, 50, 150, 150, "")

        doc.endPage()
        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)
        self.assertTrue(pdf_data.startswith(b"%PDF-"))

    def test_handle_annotations_with_sepcial_charecters_in_url(self):
        doc = self.doc
        ctx = doc.beginPage(612, 792)

        ctx.fillStyle = "blue"
        ctx.fillRect(50, 50, 300, 40)
        ctx.fillStyle = "white"
        ctx.font = "16px sans-serif"
        ctx.fillText("Link with special chars", 60, 75)

        # URL with query parameters and special characters
        special_url = "https://example.com/search?q=test&lang=en&special=äöü"
        ctx.annotateLinkUrl(50, 50, 350, 90, special_url)

        doc.endPage()
        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)

        self._test_path("pdf", "special-chars-link.pdf").write_bytes(pdf_data)

    def test_support_annotations_on_rotated_transformed_canvas(self):
        doc = self.doc
        ctx = doc.beginPage(612, 792)

        # Draw without transformation
        ctx.fillStyle = "red"
        ctx.fillRect(50, 50, 100, 40)
        ctx.annotateLinkUrl(50, 50, 150, 90, "https://example.com/normal")

        # Apply transformation and draw
        ctx.save()
        ctx.translate(300, 300)
        ctx.rotate((45 * math.pi) / 180)

        ctx.fillStyle = "blue"
        ctx.fillRect(-50, -20, 100, 40)
        # Note: Annotation coordinates should be in the transformed space
        ctx.annotateLinkUrl(-50, -20, 50, 20, "https://example.com/rotated")

        ctx.restore()

        doc.endPage()
        pdf_data = doc.close()

        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 0)

        self._test_path("pdf", "transformed-annotations.pdf").write_bytes(pdf_data)

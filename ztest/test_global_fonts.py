import platform
import sys
from pathlib import Path

import canvas_pyr

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import BaseTestCase


class GlobalFontsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        font_path = self._test_path("fonts", "SourceSerifPro-Regular.ttf")
        self.font_data = font_path.read_bytes()
        self.default_count = len(canvas_pyr.GlobalFonts.getFamilies())

    def test_get_families(self):
        canvas_pyr.GlobalFonts.getFamilies()

    def test_register_font(self):
        default_count = len(canvas_pyr.GlobalFonts.getFamilies())

        self.assertFalse(canvas_pyr.GlobalFonts.has("114514"))

        if not canvas_pyr.GlobalFonts.has("Source Serif Pro"):
            font_key = canvas_pyr.GlobalFonts.register(self.font_data)
            self.assertIsNotNone(font_key)
            self.assertEqual(
                len(canvas_pyr.GlobalFonts.getFamilies()), default_count + 1
            )
            # Verify remove returns true on first removal
            self.assertTrue(canvas_pyr.GlobalFonts.remove(font_key))  # type: ignore
        else:
            self.assertEqual(len(canvas_pyr.GlobalFonts.getFamilies()), default_count)

    def test_multipe_identical_fonts(self):
        # Register the same font multiple times
        canvas_pyr.GlobalFonts.register(self.font_data)
        count = len(canvas_pyr.GlobalFonts.getFamilies())
        canvas_pyr.GlobalFonts.register(self.font_data)
        canvas_pyr.GlobalFonts.register(self.font_data)
        self.assertEqual(
            len(canvas_pyr.GlobalFonts.getFamilies()), count
        )  # Should not increase

    def test_register_invalid_font(self):
        res = canvas_pyr.GlobalFonts.register(b"not a font")
        self.assertIsNone(res)

    def test_register_font_with_name_alias(self):
        font_alias_name = "Cascadia-skr-canvas-test"
        font_key = canvas_pyr.GlobalFonts.registerFromPath(
            str(self._test_path("fonts", "Cascadia.woff2")), font_alias_name
        )
        self.assertIsNotNone(font_key)
        style_set = next(
            (
                f
                for f in canvas_pyr.GlobalFonts.getFamilies()
                if f.family == font_alias_name
            ),
            None,
        )
        self.assertIsNotNone(style_set)
        assert style_set is not None
        self.assertEqual(
            style_set.family,
            font_alias_name,
        )
        self.assertEqual(len(style_set.styles), 1)
        self.assertEqual(
            style_set.styles[0].weight,
            400,
        )
        self.assertEqual(
            style_set.styles[0].width,
            "normal",
        )
        self.assertEqual(
            style_set.styles[0].style,
            "normal",
        )

    def test_register_fonts_from_dir(self):
        fonts_dir = self._test_path("fonts-dir")
        count = canvas_pyr.GlobalFonts.loadFontsFromDir(str(fonts_dir))
        self.assertEqual(count, 3)

    def test_register_fonts_and_remove(self):
        font_alias_name = "RegisterFromPath-RemovalTest"
        font_key = canvas_pyr.GlobalFonts.registerFromPath(
            str(self._test_path("fonts", "Lato-Regular.ttf")), font_alias_name
        )

        # Verify FontKey is returned
        self.assertIsNotNone(font_key)
        assert font_key is not None
        self.assertIsInstance(font_key.typefaceId, int)

        # Verify font exists
        style_set = next(
            (
                f
                for f in canvas_pyr.GlobalFonts.getFamilies()
                if f.family == font_alias_name
            ),
            None,
        )
        self.assertIsNotNone(style_set)
        self.assertTrue(canvas_pyr.GlobalFonts.has(font_alias_name))

        # Remove using the returned FontKey
        removed = canvas_pyr.GlobalFonts.remove(font_key)
        self.assertTrue(removed)

        # Verify font is removed
        style_set_after_removal = next(
            (
                f
                for f in canvas_pyr.GlobalFonts.getFamilies()
                if f.family == font_alias_name
            ),
            None,
        )
        self.assertIsNone(style_set_after_removal)
        self.assertFalse(canvas_pyr.GlobalFonts.has(font_alias_name))

    def test_register_from_path_with_non_existent_file(self):
        font_key = canvas_pyr.GlobalFonts.registerFromPath(
            "/non/existent/path/font.ttf"
        )
        self.assertIsNone(font_key)

    def test_multiple_removals(self):
        font_alias_name = "RemovalTest-Font"
        another_font_path = self._test_path("fonts", "SourceSerifPro-Regular.ttf")
        another_font_data = another_font_path.read_bytes()

        font_key = canvas_pyr.GlobalFonts.register(another_font_data, font_alias_name)
        self.assertIsNotNone(font_key)
        assert font_key is not None

        # Verify font exists
        style_set = next(
            (
                f
                for f in canvas_pyr.GlobalFonts.getFamilies()
                if f.family == font_alias_name
            ),
            None,
        )
        self.assertIsNotNone(style_set)
        self.assertTrue(canvas_pyr.GlobalFonts.has(font_alias_name))

        # First removal should succeed
        removed_first = canvas_pyr.GlobalFonts.remove(font_key)
        self.assertTrue(removed_first)

        # Second removal should fail since it's already removed
        removed_second = canvas_pyr.GlobalFonts.remove(font_key)
        self.assertFalse(removed_second)

    def test_remove_actually_removes_font_from_families(self):
        font_alias_name = "TrueRemovalTest-Font"
        font_path2 = self._test_path("fonts", "SourceSerifPro-Regular.ttf")
        font_data2 = font_path2.read_bytes()

        # Register font with unique alias
        font_key = canvas_pyr.GlobalFonts.register(font_data2, font_alias_name)
        self.assertIsNotNone(font_key)
        assert font_key is not None

        # Verify font exists after registration
        self.assertTrue(canvas_pyr.GlobalFonts.has(font_alias_name))

        # Remove font
        removed = canvas_pyr.GlobalFonts.remove(font_key)
        self.assertTrue(removed)

        # Verify font is no longer in families list
        style_set = next(
            (
                f
                for f in canvas_pyr.GlobalFonts.getFamilies()
                if f.family == font_alias_name
            ),
            None,
        )
        self.assertIsNone(style_set)

    def test_re_registering_font_after_removal(self):
        font_alias_name = "ReRegisterTest-Font"
        font_path2 = self._test_path("fonts", "SourceSerifPro-Regular.ttf")
        font_data2 = font_path2.read_bytes()

        # Register font
        font_key1 = canvas_pyr.GlobalFonts.register(font_data2, font_alias_name)
        self.assertIsNotNone(font_key1)
        assert font_key1 is not None
        self.assertTrue(canvas_pyr.GlobalFonts.has(font_alias_name))

        # Remove font
        self.assertTrue(canvas_pyr.GlobalFonts.remove(font_key1))
        self.assertFalse(canvas_pyr.GlobalFonts.has(font_alias_name))

        # Re-register font with same alias
        font_key2 = canvas_pyr.GlobalFonts.register(font_data2, font_alias_name)
        self.assertIsNotNone(font_key2)
        assert font_key2 is not None
        self.assertTrue(canvas_pyr.GlobalFonts.has(font_alias_name))

        # Clean up
        canvas_pyr.GlobalFonts.remove(font_key2)

    def test_font_registered_with_alias_accessible_under_both_names(self):
        font_alias_name = "DualAccess-Alias"
        original_family_name = "Source Serif Pro"
        font_path2 = self._test_path("fonts", "SourceSerifPro-Regular.ttf")
        font_data2 = font_path2.read_bytes()

        # Count styles before registration (handles pre-existing registrations from other tests)
        original_styles_before = next(
            (
                f
                for f in canvas_pyr.GlobalFonts.getFamilies()
                if f.family == original_family_name
            ),
            None,
        )
        original_styles_before_count = (
            len(original_styles_before.styles) if original_styles_before else 0
        )

        # Register font with alias
        font_key = canvas_pyr.GlobalFonts.register(font_data2, font_alias_name)
        self.assertIsNotNone(font_key)
        assert font_key is not None

        # Verify font is accessible under alias
        self.assertTrue(canvas_pyr.GlobalFonts.has(font_alias_name))

        # Verify font is also accessible under original family name
        self.assertTrue(canvas_pyr.GlobalFonts.has(original_family_name))

        # Count styles after registration (should have increased)
        original_styles_after = next(
            (
                f
                for f in canvas_pyr.GlobalFonts.getFamilies()
                if f.family == original_family_name
            ),
            None,
        )
        original_styles_after_count = (
            len(original_styles_after.styles) if original_styles_after else 0
        )
        self.assertTrue(original_styles_after_count > original_styles_before_count)

        # Remove font
        canvas_pyr.GlobalFonts.remove(font_key)

        # Verify alias is gone
        self.assertFalse(canvas_pyr.GlobalFonts.has(font_alias_name))

        # Verify style count returned to original (our registration's style was removed)
        original_styles_after_remove = next(
            (
                f
                for f in canvas_pyr.GlobalFonts.getFamilies()
                if f.family == original_family_name
            ),
            None,
        )
        original_styles_after_remove_count = (
            len(original_styles_after_remove.styles)
            if original_styles_after_remove
            else 0
        )
        self.assertEqual(
            original_styles_after_remove_count, original_styles_before_count
        )

    def test_collision_dedupe_bypass_fix(self):
        # This tests the collision bypass fix where removing a font at the base hash slot
        # would break the probe chain and cause a displaced font to get a new ID on re-registration
        #
        # Scenario being tested:
        # 1. Font A registers with hash H -> gets ID H
        # 2. Font B registers with same hash H -> collision -> gets ID H+1
        # 3. Font A is removed (erase(H) - full deletion, no tombstone)
        # 4. Font B re-registers -> should find existing entry via secondary index, not create duplicate

        font_a_alias = "CollisionTest-FontA"
        font_b_alias = "CollisionTest-FontB"

        # Use two different fonts so they have different content hashes
        # (In a real collision scenario, they'd have the same hash but different content)
        font_a_path = self._test_path("fonts", "SourceSerifPro-Regular.ttf")
        font_b_path = self._test_path("fonts", "Cascadia.woff2")
        font_a_data = font_a_path.read_bytes()
        font_b_data = font_b_path.read_bytes()

        # Register font A
        font_key_a = canvas_pyr.GlobalFonts.register(font_a_data, font_a_alias)
        self.assertIsNotNone(font_key_a)

        # Register font B
        font_key_b1 = canvas_pyr.GlobalFonts.register(font_b_data, font_b_alias)
        self.assertIsNotNone(font_key_b1)
        assert font_key_b1 is not None

        # Store the internal ID of font B for comparison
        font_b_id1 = font_key_b1.typefaceId
        self.assertIsInstance(font_b_id1, int)

        # Remove font A (this would break probe chain in the old implementation)
        self.assertTrue(canvas_pyr.GlobalFonts.remove(font_key_a))  # type: ignore

        # Re-register font B - should find existing entry and return same ID
        font_key_b2 = canvas_pyr.GlobalFonts.register(font_b_data, font_b_alias)
        self.assertIsNotNone(font_key_b2)
        assert font_key_b2 is not None

        # The key insight: the ID should be the same, not a new one
        font_b_id2 = font_key_b2.typefaceId
        self.assertEqual(font_b_id2, font_b_id1)

        # Verify only one instance of font B exists in families
        font_b_families = [
            f for f in canvas_pyr.GlobalFonts.getFamilies() if f.family == font_b_alias
        ]
        self.assertEqual(len(font_b_families), 1)

        # Clean up
        canvas_pyr.GlobalFonts.remove(font_key_b2)

    def test_remove_batch(self):
        # Use different font files to ensure they get different typeface IDs
        font_data1 = self._test_path("fonts", "SourceSerifPro-Regular.ttf").read_bytes()
        font_data2 = self._test_path("fonts", "Cascadia.woff2").read_bytes()
        font_data3 = self._test_path("fonts", "Lato-Regular.ttf").read_bytes()

        # Register multiple fonts with unique aliases
        font_key1 = canvas_pyr.GlobalFonts.register(font_data1, "BatchTest-Font1")
        font_key2 = canvas_pyr.GlobalFonts.register(font_data2, "BatchTest-Font2")
        font_key3 = canvas_pyr.GlobalFonts.register(font_data3, "BatchTest-Font3")

        self.assertIsNotNone(font_key1)
        self.assertIsNotNone(font_key2)
        self.assertIsNotNone(font_key3)
        assert font_key1 is not None and font_key2 is not None and font_key3 is not None

        # Verify all have different typeface IDs (different fonts)
        self.assertNotEqual(font_key1.typefaceId, font_key2.typefaceId)
        self.assertNotEqual(font_key2.typefaceId, font_key3.typefaceId)
        self.assertNotEqual(font_key1.typefaceId, font_key3.typefaceId)

        # Verify all exist
        self.assertTrue(canvas_pyr.GlobalFonts.has("BatchTest-Font1"))
        self.assertTrue(canvas_pyr.GlobalFonts.has("BatchTest-Font2"))
        self.assertTrue(canvas_pyr.GlobalFonts.has("BatchTest-Font3"))

        # Remove all in batch
        removed_count = canvas_pyr.GlobalFonts.removeBatch(
            [font_key1, font_key2, font_key3]
        )
        self.assertEqual(removed_count, 3)

        # Verify all are gone
        self.assertFalse(canvas_pyr.GlobalFonts.has("BatchTest-Font1"))
        self.assertFalse(canvas_pyr.GlobalFonts.has("BatchTest-Font2"))
        self.assertFalse(canvas_pyr.GlobalFonts.has("BatchTest-Font3"))

    def test_remove_batch_with_stale_key(self):
        font_path2 = self._test_path("fonts", "SourceSerifPro-Regular.ttf")
        font_data2 = font_path2.read_bytes()

        # Register and then remove a font to get a stale key
        font_key = canvas_pyr.GlobalFonts.register(font_data2, "StaleKeyTest-Font")
        self.assertIsNotNone(font_key)
        assert font_key is not None
        self.assertTrue(canvas_pyr.GlobalFonts.remove(font_key))

        # Try to remove with stale key - should return 0
        removed_count = canvas_pyr.GlobalFonts.removeBatch([font_key])
        self.assertEqual(removed_count, 0)

    def test_remove_batch_with_empty_array(self):
        removed_count = canvas_pyr.GlobalFonts.removeBatch([])
        self.assertEqual(removed_count, 0)

    def test_remove_all(self):
        font_path2 = self._test_path("fonts", "SourceSerifPro-Regular.ttf")
        font_data2 = font_path2.read_bytes()

        # Register some fonts
        font_key1 = canvas_pyr.GlobalFonts.register(font_data2, "RemoveAllTest-Font1")
        font_key2 = canvas_pyr.GlobalFonts.register(font_data2, "RemoveAllTest-Font2")

        self.assertIsNotNone(font_key1)
        self.assertIsNotNone(font_key2)

        # Get count of registered fonts (excluding system fonts - check for our test fonts)
        self.assertTrue(canvas_pyr.GlobalFonts.has("RemoveAllTest-Font1"))
        self.assertTrue(canvas_pyr.GlobalFonts.has("RemoveAllTest-Font2"))

        # Remove all
        removed_count = canvas_pyr.GlobalFonts.removeAll()
        self.assertTrue(removed_count >= 2)

        # Verify our test fonts are gone
        self.assertFalse(canvas_pyr.GlobalFonts.has("RemoveAllTest-Font1"))
        self.assertFalse(canvas_pyr.GlobalFonts.has("RemoveAllTest-Font2"))

    def test_set_alias_non_existent_font(self):
        result = canvas_pyr.GlobalFonts.setAlias("NonExistentFont12345", "MyAlias")
        self.assertFalse(result)

    def test_set_alias_existing_font(self):
        # Register a font first
        font_path2 = self._test_path("fonts", "SourceSerifPro-Regular.ttf")
        font_data2 = font_path2.read_bytes()
        font_key = canvas_pyr.GlobalFonts.register(font_data2, "SetAliasTest-Font")
        self.assertIsNotNone(font_key)

        # Set alias should succeed
        result = canvas_pyr.GlobalFonts.setAlias(
            "SetAliasTest-Font", "SetAliasTest-Alias"
        )
        self.assertTrue(result)

        # Clean up
        canvas_pyr.GlobalFonts.remove(font_key)  # type: ignore

    def test_stale_aliases_should_not_transfer(self):
        font_a_path = self._test_path("fonts", "SourceSerifPro-Regular.ttf")
        font_b_path = self._test_path("fonts", "Cascadia.woff2")
        font_a_data = font_a_path.read_bytes()
        font_b_data = font_b_path.read_bytes()

        # Step 1: Register Font A with alias "StaleAliasTest"
        font_key_a = canvas_pyr.GlobalFonts.register(font_a_data, "StaleAliasTest")
        self.assertIsNotNone(font_key_a)

        # Step 2: Set an alias pointing to "StaleAliasTest"
        alias_set = canvas_pyr.GlobalFonts.setAlias("StaleAliasTest", "StaleAliasX")
        self.assertTrue(alias_set)

        # Verify alias exists
        self.assertTrue(canvas_pyr.GlobalFonts.has("StaleAliasX"))

        # Step 3: Remove Font A
        self.assertTrue(canvas_pyr.GlobalFonts.remove(font_key_a))  # type: ignore

        # Verify alias is gone (font was removed)
        self.assertFalse(canvas_pyr.GlobalFonts.has("StaleAliasX"))

        # Step 4: Register Font B with the SAME alias name "StaleAliasTest"
        font_key_b = canvas_pyr.GlobalFonts.register(font_b_data, "StaleAliasTest")
        self.assertIsNotNone(font_key_b)

        # Step 5: Verify "StaleAliasX" does NOT exist (the stale alias should NOT transfer)
        self.assertFalse(canvas_pyr.GlobalFonts.has("StaleAliasX"))

        # Step 6: Register and remove an unrelated font to trigger rebuild
        font_key_c = canvas_pyr.GlobalFonts.register(font_a_data, "UnrelatedFont")
        canvas_pyr.GlobalFonts.remove(font_key_c)  # type: ignore

        # Step 7: Verify "StaleAliasX" STILL does not exist after rebuild
        self.assertFalse(canvas_pyr.GlobalFonts.has("StaleAliasX"))

        # Clean up
        canvas_pyr.GlobalFonts.remove(font_key_b)  # type: ignore

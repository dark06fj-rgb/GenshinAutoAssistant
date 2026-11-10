import unittest

from scripts.sync_quest_source_metadata import classify_unresolved_title


class UnresolvedQuestTitleClassificationTests(unittest.TestCase):
    def test_unreleased_marker_is_excluded(self):
        self.assertEqual(
            classify_unresolved_title("农民的宝藏$UNRELEASED", 4129559335),
            "unreleased_or_internal",
        )

    def test_test_placeholder_is_excluded(self):
        self.assertEqual(
            classify_unresolved_title("（test）旅行画家-全对话", 1769442903),
            "internal_test",
        )

    def test_missing_hash_and_title_is_not_translatable(self):
        self.assertEqual(classify_unresolved_title("", 0), "no_source_title")

    def test_real_title_without_english_fallback_remains_unresolved(self):
        self.assertEqual(
            classify_unresolved_title("农民的宝藏", 4129559335),
            "missing_english_title",
        )


if __name__ == "__main__":
    unittest.main()

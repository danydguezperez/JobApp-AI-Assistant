import unittest

from jobapp_ai_assistant import migrate_llm_settings


class LlmModelMigrationTests(unittest.TestCase):
    def test_deprecated_gemini_is_migrated_and_valid_models_are_kept(self) -> None:
        settings = {
            "providers": {
                "gemini": {"model": "gemini-3.5-flash"},
                "openai": {"model": "gpt-5.6-terra"},      # valid current ID
                "anthropic": {"model": "claude-sonnet-5"},  # valid current ID
            }
        }
        changed = migrate_llm_settings(settings)
        self.assertTrue(changed)
        self.assertEqual(settings["providers"]["gemini"]["model"], "gemini-2.5-flash")
        self.assertEqual(settings["providers"]["openai"]["model"], "gpt-5.6-terra")
        self.assertEqual(settings["providers"]["anthropic"]["model"], "claude-sonnet-5")

    def test_current_models_are_left_unchanged(self) -> None:
        settings = {"providers": {"gemini": {"model": "gemini-2.5-flash"}}}
        self.assertFalse(migrate_llm_settings(settings))


if __name__ == "__main__":
    unittest.main()

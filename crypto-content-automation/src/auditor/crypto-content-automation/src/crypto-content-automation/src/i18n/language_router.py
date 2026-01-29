# Copyright 2026 GEORGI STOEDINOV VLADIMIROV
# Licensed under the Apache License, Version 2.0

from typing import Dict, List


class LanguageRouter:
    """
    Routes and translates content to multiple languages.
    Works after verification and before publishing.
    """

    def __init__(self, translator):
        self.translator = translator

    def translate_all(self, text: str, languages: List[str]) -> Dict[str, str]:
        results = {}
        for lang in languages:
            if lang == "en":
                results["en"] = text
            else:
                results[lang] = self.translator.translate(text, target_lang=lang)
        return results


class BaseTranslator:
    def translate(self, text: str, target_lang: str) -> str:
        raise NotImplementedError

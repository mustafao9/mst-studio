#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

class I18nEngine:
    def __init__(self, locales_dir="locales", default_lang="tr"):
        self.locales_dir = locales_dir
        self.current_lang = default_lang
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        file_path = os.path.join(self.locales_dir, f"{self.current_lang}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        else:
            self.translations = {}

    def set_language(self, lang_code):
        if self.current_lang != lang_code:
            self.current_lang = lang_code
            self.load_translations()

    def get(self, key, default_text=""):
        return self.translations.get(key, default_text or key)

# Global Tekil Örnek (Singleton)
i18n = I18nEngine()

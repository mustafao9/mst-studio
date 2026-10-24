#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest
from core.theme_engine import MSTThemeEngine

class TestMSTThemeEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MSTThemeEngine()

    def test_theme_loading(self):
        colors_light = self.engine.load_theme("light")
        self.assertEqual(colors_light["theme_name"], "light")
        self.assertIn("bg_main", colors_light)

        colors_dark = self.engine.load_theme("dark")
        self.assertEqual(colors_dark["theme_name"], "dark")
        self.assertEqual(colors_dark["bg_main"], "#1e1e1e")

if __name__ == '__main__':
    unittest.main()

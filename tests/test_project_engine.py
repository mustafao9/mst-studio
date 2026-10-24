#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest
from core.project_engine import MSTProjectEngine

class TestMSTProjectEngine(unittest.TestCase):
    def setUp(self):
        self.test_file = "tests/temp_test_project.mst"
        self.engine = MSTProjectEngine("Test_Otomasyon")
        self.engine.pages = {"Giris": {"is_login": True, "role": "Herkes"}}
        self.engine.page_components = {
            "Giris": [{"id": 1, "type": "Metin Kutusu", "x": 10, "y": 10, "w": 100, "h": 30}]
        }

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(f"{self.test_file}.tmp"):
            os.remove(f"{self.test_file}.tmp")

    def test_save_and_load(self):
        # Kaydetme Testi
        saved = self.engine.save_project(self.test_file)
        self.assertTrue(saved)
        self.assertTrue(os.path.exists(self.test_file))

        # Yükleme Testi
        new_engine = MSTProjectEngine()
        loaded = new_engine.load_project(self.test_file)
        self.assertTrue(loaded)
        self.assertEqual(new_engine.project_name, "Test_Otomasyon")
        self.assertIn("Giris", new_engine.pages)
        self.assertEqual(len(new_engine.page_components["Giris"]), 1)

if __name__ == '__main__':
    unittest.main()

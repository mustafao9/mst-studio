#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from core.form_generator import MSTFormGenerator

class TestMSTFormGenerator(unittest.TestCase):
    def test_form_generation(self):
        cols = [
            {"name": "id", "type": "INTEGER"},
            {"name": "ad_soyad", "type": "TEXT"},
            {"name": "sehir", "type": "TEXT"}
        ]
        comps = MSTFormGenerator.generate_form_for_table("musteriler", cols)

        self.assertTrue(len(comps) > 0)
        
        # Etiket, Metin Kutusu, Açılır Liste ve Buton varlık denetimi
        types = [c["type"] for c in comps]
        self.assertIn("Etiket", types)
        self.assertIn("Metin Kutusu", types)
        self.assertIn("Açılır Liste", types)
        self.assertIn("Buton", types)
        self.assertIn("Veri Tablosu", types)

if __name__ == '__main__':
    unittest.main()

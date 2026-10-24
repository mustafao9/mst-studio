#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import unittest
from core.db_engine import DatabaseEngine
from core.report_engine import MSTReportEngine

class TestMSTReportEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_report_output"
        self.db_path = "tests/temp_report_db.db"
        self.db_engine = DatabaseEngine(self.db_path)
        self.report_engine = MSTReportEngine(self.db_engine)

        # Test verisi hazırlığı
        self.db_engine.create_table("urunler", [
            {"name": "urun_adi", "type": "TEXT"},
            {"name": "fiyati", "type": "REAL"}
        ])
        self.db_engine.execute_query("INSERT INTO urunler (urun_adi, fiyati) VALUES (?, ?)", ("Ekmek", 10.5))
        self.db_engine.execute_query("INSERT INTO urunler (urun_adi, fiyati) VALUES (?, ?)", ("Süt", 25.0))

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_export_csv(self):
        csv_path = os.path.join(self.test_dir, "test_report.csv")
        res_path = self.report_engine.export_to_csv("urunler", csv_path)
        self.assertTrue(os.path.exists(res_path))
        
        with open(res_path, "r", encoding="utf-8-sig") as f:
            content = f.read()
            self.assertIn("urun_adi", content)
            self.assertIn("Ekmek", content)

    def test_export_json(self):
        json_path = os.path.join(self.test_dir, "test_report.json")
        res_path = self.report_engine.export_to_json("urunler", json_path)
        self.assertTrue(os.path.exists(res_path))

        with open(res_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Süt", content)

    def test_export_html(self):
        html_path = os.path.join(self.test_dir, "test_report.html")
        res_path = self.report_engine.export_to_html("urunler", html_path, title="Ürün Listesi Raporu")
        self.assertTrue(os.path.exists(res_path))

        with open(res_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("<title>Ürün Listesi Raporu</title>", content)
            self.assertIn("Ekmek", content)

if __name__ == '__main__':
    unittest.main()

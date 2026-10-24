#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import unittest
from core.project_engine import MSTProjectEngine
from core.db_engine import DatabaseEngine
from core.packager_engine import MSTPackagerEngine

class TestMSTPackagerEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_packager_output"
        self.db_path = "tests/temp_packager_db.db"
        
        self.project_engine = MSTProjectEngine("Test_Packager_App")
        self.project_engine.pages = {"Giris_Sayfasi": {"is_login": True, "role": "Herkes"}}
        self.project_engine.page_components = {"Giris_Sayfasi": []}
        
        self.db_engine = DatabaseEngine(self.db_path)
        self.packager = MSTPackagerEngine(self.project_engine, self.db_engine)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_build_package(self):
        built_dir = self.packager.build_package(self.test_dir, "Test_Packager_App")
        self.assertTrue(os.path.exists(built_dir))
        self.assertTrue(os.path.exists(os.path.join(built_dir, "app_data.mst")))
        self.assertTrue(os.path.exists(os.path.join(built_dir, "manifest.json")))
        self.assertTrue(os.path.exists(os.path.join(built_dir, "runner.py")))

if __name__ == '__main__':
    unittest.main()

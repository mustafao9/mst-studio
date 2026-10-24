#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest
from core.db_engine import DatabaseEngine

class TestMSTDataEditorLogic(unittest.TestCase):
    def setUp(self):
        self.db_path = "tests/temp_editor_db.db"
        self.db = DatabaseEngine(self.db_path)
        self.db.create_table("kategoriler", [{"name": "kategori_adi", "type": "TEXT"}])

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_insert_update_delete(self):
        # Insert
        self.db.execute_query("INSERT INTO kategoriler (kategori_adi) VALUES (?)", ("Elektronik",))
        cursor = self.db.execute_query("SELECT * FROM kategoriler WHERE kategori_adi = ?", ("Elektronik",))
        res = cursor.fetchone()
        self.assertIsNotNone(res)

        # Update
        self.db.execute_query("UPDATE kategoriler SET kategori_adi = ? WHERE id = ?", ("Giyim", res[0]))
        cursor = self.db.execute_query("SELECT kategori_adi FROM kategoriler WHERE id = ?", (res[0],))
        self.assertEqual(cursor.fetchone()[0], "Giyim")

        # Delete
        self.db.execute_query("DELETE FROM kategoriler WHERE id = ?", (res[0],))
        cursor = self.db.execute_query("SELECT COUNT(*) FROM kategoriler")
        self.assertEqual(cursor.fetchone()[0], 0)

if __name__ == '__main__':
    unittest.main()

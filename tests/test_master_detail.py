#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import unittest
from core.db_engine import DatabaseEngine

class TestMasterDetailLogic(unittest.TestCase):
    def setUp(self):
        self.db_path = "tests/temp_master_detail_db.db"
        self.db = DatabaseEngine(self.db_path)

        # Master Table: Müşteriler
        self.db.create_table("musteriler", [{"name": "ad_soyad", "type": "TEXT"}])
        # Detail Table: Siparişler (musteri_id foreign key)
        self.db.create_table("siparisler", [
            {"name": "musteri_id", "type": "INTEGER"},
            {"name": "urun_adi", "type": "TEXT"},
            {"name": "tutar", "type": "REAL"}
        ])

        # Örnek Veri
        self.db.execute_query("INSERT INTO musteriler (ad_soyad) VALUES (?)", ("Mustafa",))
        self.db.execute_query("INSERT INTO musteriler (ad_soyad) VALUES (?)", ("Ahmet",))

        self.db.execute_query("INSERT INTO siparisler (musteri_id, urun_adi, tutar) VALUES (?, ?, ?)", (1, "Laptoptan", 15000))
        self.db.execute_query("INSERT INTO siparisler (musteri_id, urun_adi, tutar) VALUES (?, ?, ?)", (1, "Mouse", 350))
        self.db.execute_query("INSERT INTO siparisler (musteri_id, urun_adi, tutar) VALUES (?, ?, ?)", (2, "Klavyen", 800))

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_detail_filtering(self):
        # Müşteri 1'in siparişlerini çek
        cursor = self.db.execute_query("SELECT * FROM siparisler WHERE musteri_id = ?", (1,))
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 2)

        # Müşteri 2'nin siparişlerini çek
        cursor = self.db.execute_query("SELECT * FROM siparisler WHERE musteri_id = ?", (2,))
        rows_2 = cursor.fetchall()
        self.assertEqual(len(rows_2), 1)

if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from core.query_builder import MSTQueryBuilder

class TestMSTQueryBuilder(unittest.TestCase):
    def test_query_building(self):
        builder = MSTQueryBuilder("musteriler")
        builder.add_join("INNER", "sehirler", "musteriler.sehir_id", "sehirler.id")
        builder.add_column("musteriler", "ad_soyad", "Müşteri Adı")
        builder.add_column("sehirler", "sehir_adi", "Şehir")
        builder.add_calculated_column("fiyat * adet", "Toplam")
        builder.add_where("musteriler.yas", ">=", "18")

        sql = builder.build_sql()

        self.assertIn("SELECT musteriler.ad_soyad AS [Müşteri Adı]", sql)
        self.assertIn("INNER JOIN sehirler ON musteriler.sehir_id = sehirler.id", sql)
        self.assertIn("(fiyat * adet) AS [Toplam]", sql)
        self.assertIn("WHERE musteriler.yas >= '18'", sql)

if __name__ == '__main__':
    unittest.main()

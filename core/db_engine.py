#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

class DatabaseEngine:
    """MST Studio SQLite Veritabanı Yönetim Motoru."""

    def __init__(self, db_path):
        self.db_path = db_path
        self._ensure_db_dir()

    def _ensure_db_dir(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute_query(self, sql, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor

    def sanitize(self, name):
        """SQL Enjeksiyonuna karşı tablo ve sütun isimlerini temizler."""
        if not name:
            return ""
        return "".join([c for c in str(name) if c.isalnum() or c == '_'])

    def get_tables(self):
        """Veritabanındaki tablo isimlerini liste olarak döndürür."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables

    def get_table_columns(self, table_name):
        """Belirtilen tablonun sütun bilgilerini döndürür."""
        clean_name = self.sanitize(table_name)
        if not clean_name:
            return []

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({clean_name});")
        rows = cursor.fetchall()
        conn.close()

        cols = []
        for r in rows:
            cols.append({
                "cid": r[0],
                "name": r[1],
                "type": r[2],
                "notnull": r[3],
                "dflt_value": r[4],
                "pk": r[5]
            })
        return cols

    def get_table_data(self, table_name):
        """Belirtilen tablodaki tüm satırları sözlük listesi olarak döndürür."""
        clean_name = self.sanitize(table_name)
        if not clean_name:
            return []

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {clean_name};")
        rows = cursor.fetchall()
        conn.close()

        return [dict(r) for r in rows]

    def create_table(self, table_name, columns):
        clean_name = self.sanitize(table_name)
        col_defs = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        for col in columns:
            c_name = self.sanitize(col.get("name"))
            c_type = col.get("type", "TEXT")
            if c_name and c_name != "id":
                col_defs.append(f"{c_name} {c_type}")

        sql = f"CREATE TABLE IF NOT EXISTS {clean_name} ({', '.join(col_defs)});"
        self.execute_query(sql)

    def drop_table(self, table_name):
        clean_name = self.sanitize(table_name)
        if clean_name:
            self.execute_query(f"DROP TABLE IF EXISTS {clean_name};")

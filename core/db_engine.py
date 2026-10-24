#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import re
from core.security_engine import SecurityEngine

class DatabaseEngine:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_system_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def sanitize(self, text):
        tr_map = {'ç': 'c', 'Ç': 'c', 'ğ': 'g', 'Ğ': 'g', 'ı': 'i', 'İ': 'i', 'ö': 'o', 'Ö': 'o', 'ş': 's', 'Ş': 's', 'ü': 'u', 'Ü': 'u'}
        for k, v in tr_map.items():
            text = text.replace(k, v)
        text = text.strip().replace(" ", "_").replace("-", "_")
        return re.sub(r'[^a-zA-Z0-9_]', '', text)

    def init_system_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kullanicilar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad_soyad TEXT,
                    kullanici_adi TEXT UNIQUE,
                    sifre TEXT,
                    rol TEXT
                )
            ''')
            
            cursor.execute("SELECT COUNT(*) FROM kullanicilar")
            if cursor.fetchone()[0] == 0:
                hashed_pw = SecurityEngine.hash_password("123")
                cursor.execute(
                    "INSERT INTO kullanicilar (ad_soyad, kullanici_adi, sifre, rol) VALUES (?, ?, ?, ?)",
                    ("Sistem Yöneticisi", "admin", hashed_pw, "Admin")
                )
            conn.commit()

    def get_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            return [t[0] for t in cursor.fetchall()]

    def get_table_columns(self, table_name):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            return [{"id": col[0], "name": col[1], "type": col[2], "notnull": col[3], "pk": col[5]} for col in cursor.fetchall()]

    def create_table(self, table_name, columns_def, foreign_keys=None):
        t_name = self.sanitize(table_name)
        cols_sql = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]

        for col in columns_def:
            c_name = self.sanitize(col['name'])
            c_type = col.get('type', 'TEXT')
            if c_name.lower() != 'id':
                cols_sql.append(f"{c_name} {c_type}")

        if foreign_keys:
            for fk in foreign_keys:
                cols_sql.append(f"FOREIGN KEY ({self.sanitize(fk['column'])}) REFERENCES {self.sanitize(fk['ref_table'])}({self.sanitize(fk['ref_column'])}) ON DELETE CASCADE")

        sql = f"CREATE TABLE IF NOT EXISTS {t_name} ({', '.join(cols_sql)});"
        with self.get_connection() as conn:
            conn.cursor().execute(sql)
            conn.commit()
        return t_name

    def drop_table(self, table_name):
        with self.get_connection() as conn:
            conn.cursor().execute(f"DROP TABLE IF EXISTS {self.sanitize(table_name)};")
            conn.commit()

    def execute_query(self, sql, params=()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            return cursor

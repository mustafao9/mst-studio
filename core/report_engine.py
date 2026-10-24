#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import json
import sqlite3

class MSTReportEngine:
    """Veritabanı verilerini ve sorgu sonuçlarını CSV, HTML (PDF uyumlu) ve JSON formatlarında raporlayan motor."""

    def __init__(self, db_engine):
        self.db = db_engine

    def _fetch_table_data(self, table_name_or_query, params=()):
        """Verilen tablo adı veya SQL sorgusu üzerinden verileri ve sütun başlıklarını döndürür."""
        clean_input = table_name_or_query.strip()
        if " " not in clean_input and not clean_input.upper().startswith("SELECT"):
            sql = f"SELECT * FROM {self.db.sanitize(clean_input)}"
        else:
            sql = clean_input

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return columns, rows

    def export_to_csv(self, table_name_or_query, output_path, params=()):
        """Verileri MS Excel uyumlu UTF-8-SIG CSV formatında dışa aktarır."""
        columns, rows = self._fetch_table_data(table_name_or_query, params)
        
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(columns)
            writer.writerows(rows)
            
        return output_path

    def export_to_json(self, table_name_or_query, output_path, params=()):
        """Verileri JSON formatında dışa aktarır."""
        columns, rows = self._fetch_table_data(table_name_or_query, params)
        data = [dict(zip(columns, row)) for row in rows]

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, mode="w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return output_path

    def export_to_html(self, table_name_or_query, output_path, title="MST Studio Rapor Çıktısı", params=()):
        """Yazdırılabilir ve PDF çıktısına dönüştürülebilir stilize HTML rapor oluşturur."""
        columns, rows = self._fetch_table_data(table_name_or_query, params)

        headers_html = "".join([f"<th>{col}</th>" for col in columns])
        rows_html = ""
        for row in rows:
            cols_html = "".join([f"<td>{val if val is not None else ''}</td>" for val in row])
            rows_html += f"<tr>{cols_html}</tr>\n"

        html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #ffffff; color: #333; }}
        h2 {{ color: #007acc; border-bottom: 2px solid #007acc; padding-bottom: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ border: 1px solid #dddddd; text-align: left; padding: 8px; font-size: 13px; }}
        th {{ background-color: #007acc; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .footer {{ margin-top: 20px; font-size: 11px; color: #777; text-align: right; }}
    </style>
</head>
<body>
    <h2>📊 {title}</h2>
    <table>
        <thead>
            <tr>{headers_html}</tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    <div class="footer">MST Studio Raporlama Engine Tarafından Üretilmiştir.</div>
</body>
</html>"""

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, mode="w", encoding="utf-8") as f:
            f.write(html_content)

        return output_path

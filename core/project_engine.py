#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import hashlib
import shutil

class MSTProjectEngine:
    FORMAT_VERSION = "1.0.0"

    def __init__(self, project_name="Yeni_Proje"):
        self.project_name = project_name
        self.file_path = None
        self.metadata = {
            "app_name": project_name,
            "version": "1.0.0",
            "mst_format_version": self.FORMAT_VERSION,
            "author": "Mustafa Satılmış"
        }
        self.database_schema = {}
        self.pages = {}
        self.page_components = {}
        self.roles = ["Admin", "Kasiyer", "Herkes"]

    def to_dict(self):
        content = {
            "manifest": self.metadata,
            "database_schema": self.database_schema,
            "pages": self.pages,
            "page_components": self.page_components,
            "roles": self.roles
        }
        raw_json = json.dumps(content, sort_keys=True, ensure_ascii=False)
        content["manifest"]["digest"] = hashlib.sha256(raw_json.encode('utf-8')).hexdigest()
        return content

    def save_project(self, file_path):
        self.file_path = file_path
        data = self.to_dict()
        tmp_path = f"{file_path}.tmp"

        # Atomik Yazma: Önce geçici dosyaya yaz, sonra değiştir
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        shutil.move(tmp_path, file_path)
        return True

    def load_project(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Proje dosyası bulunamadı: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        manifest = data.get("manifest", {})
        fmt_ver = manifest.get("mst_format_version", "0.0.0")

        if fmt_ver != self.FORMAT_VERSION:
            # İleride geriye dönük uyumluluk dönüşümleri burada yapılacak
            pass

        self.file_path = file_path
        self.metadata = manifest
        self.database_schema = data.get("database_schema", {})
        self.pages = data.get("pages", {})
        self.page_components = data.get("page_components", {})
        self.roles = data.get("roles", ["Admin", "Herkes"])
        self.project_name = manifest.get("app_name", "Yüklenen_Proje")
        return True

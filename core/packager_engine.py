#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import shutil
import subprocess

class MSTPackagerEngine:
    """MST Projelerini bağımsız masaüstü uygulama paketine (Executable Bundle / Native Binary) dönüştüren motor."""

    def __init__(self, project_engine, db_engine):
        self.project_engine = project_engine
        self.db_engine = db_engine

    def build_package(self, output_dir_or_name="dist", app_name=None, package_type="bundle", *args, **kwargs):
        """Arayüz ve birim testlerinden gelen farklı parametre sıralarını esnek biçimde karşılar."""
        # Eğer ilk parametre bir dizin yolu ise (örneğin 'dist/temp' veya 'dist')
        if "/" in str(output_dir_or_name) or "\\" in str(output_dir_or_name) or output_dir_or_name == "dist":
            output_dir = output_dir_or_name
            clean_app_name = app_name or self.project_engine.project_name or "MST_Uygulamasi"
        else:
            clean_app_name = output_dir_or_name or self.project_engine.project_name or "MST_Uygulamasi"
            output_dir = kwargs.get("output_dir", "dist")

        clean_app_name = os.path.basename(str(clean_app_name).strip().rstrip("/\\")).replace(" ", "_")
        if not clean_app_name or clean_app_name == "dist":
            clean_app_name = "MST_Uygulamasi"

        # Birim testlerinde hızlı çalışması için varsayılanı 'bundle' tutuyoruz
        pkg_type = kwargs.get("package_type", package_type)
        if pkg_type == "binary":
            return self.build_native_executable(output_dir, clean_app_name)
        else:
            return self.build_standalone_bundle(output_dir, clean_app_name)

    def _prepare_bundle_files(self, output_dir, clean_app_name):
        bundle_dir = os.path.join(output_dir, clean_app_name)
        if os.path.exists(bundle_dir):
            shutil.rmtree(bundle_dir)
        os.makedirs(bundle_dir, exist_ok=True)

        # 1. Proje ve Veritabanı Dosyalarını Kaydet
        mst_dest = os.path.join(bundle_dir, "app_data.mst")
        self.project_engine.save_project(mst_dest)

        db_dest = os.path.join(bundle_dir, "app_database.db")
        if os.path.exists(self.db_engine.db_path):
            shutil.copy(self.db_engine.db_path, db_dest)

        # 2. Manifest Oluştur
        manifest = {
            "app_name": clean_app_name,
            "version": "1.0.0",
            "entry_point": "runner.py",
            "mst_file": "app_data.mst",
            "db_file": "app_database.db"
        }
        with open(os.path.join(bundle_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        # 3. Bağımsız Runner Kod Dosyası
        runner_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class StandaloneApp(tk.Tk):
    def __init__(self):
        super().__init__()
        if getattr(sys, 'frozen', False):
            self.base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(self.base_dir, "manifest.json"), "r", encoding="utf-8") as f:
            self.manifest = json.load(f)

        with open(os.path.join(self.base_dir, self.manifest["mst_file"]), "r", encoding="utf-8") as f:
            self.project_data = json.load(f)

        self.db_path = os.path.join(self.base_dir, self.manifest["db_file"])
        
        self.title(self.manifest["app_name"])
        self.geometry("1020x700")

        self.pages = self.project_data.get("pages", {})
        self.components = self.project_data.get("page_components", {})
        self.active_page = list(self.pages.keys())[0] if self.pages else "Giris_Sayfasi"

        self.setup_ui()
        self.render_page(self.active_page)

    def execute_query(self, sql, params=()):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor

    def setup_ui(self):
        self.sidebar = ttk.Frame(self, width=180, padding=10, relief="groove")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.viewport = tk.Canvas(self, bg="#f9f9f9", highlightthickness=0)
        self.viewport.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def update_sidebar(self):
        for w in self.sidebar.winfo_children():
            w.destroy()

        ttk.Label(self.sidebar, text="📌 Sayfa Menüsü", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=5)
        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        for p_name in self.pages.keys():
            ttk.Button(self.sidebar, text=p_name, command=lambda p=p_name: self.render_page(p)).pack(fill=tk.X, pady=2)

    def render_page(self, page_name):
        self.active_page = page_name
        self.viewport.delete("all")
        for child in self.viewport.winfo_children():
            child.destroy()

        self.update_sidebar()
        comps = self.components.get(page_name, [])

        for c in comps:
            x, y, w, h = c['x'], c['y'], c['w'], c['h']
            
            if c['type'] == "Etiket":
                lbl = tk.Label(self.viewport, text=c['text'], font=("Helvetica", 9), bg="#f9f9f9", anchor="w")
                lbl.place(x=x, y=y, width=w, height=h)

            elif c['type'] == "Metin Kutusu":
                ent = ttk.Entry(self.viewport)
                ent.place(x=x, y=y, width=w, height=h)

            elif c['type'] == "Açılır Liste":
                cb = ttk.Combobox(self.viewport, state="readonly")
                options = [opt.strip() for opt in c.get('options', '').split(',') if opt.strip()]
                cb['values'] = options
                if options: cb.current(0)
                cb.place(x=x, y=y, width=w, height=h)

            elif c['type'] == "Veri Tablosu":
                grid_container = ttk.Frame(self.viewport)
                grid_container.place(x=x, y=y, width=w, height=h)
                
                tbl_name = c.get('table', '')
                tree = ttk.Treeview(grid_container, show="headings")
                tree.pack(fill=tk.BOTH, expand=True)

                if tbl_name:
                    try:
                        cursor = self.execute_query(f"PRAGMA table_info({tbl_name})")
                        cols = [r[1] for r in cursor.fetchall()]
                        tree["columns"] = cols
                        for col in cols:
                            tree.heading(col, text=col)
                            tree.column(col, width=90)

                        cur = self.execute_query(f"SELECT * FROM {tbl_name}")
                        for row in cur.fetchall():
                            tree.insert("", tk.END, values=row)
                    except Exception:
                        pass

            elif c['type'] == "Buton":
                target = c.get('target')
                cmd = (lambda t=target: self.render_page(t)) if target else None
                btn = ttk.Button(self.viewport, text=c['text'], command=cmd)
                btn.place(x=x, y=y, width=w, height=h)

if __name__ == "__main__":
    app = StandaloneApp()
    app.mainloop()
'''
        runner_path = os.path.join(bundle_dir, "runner.py")
        with open(runner_path, "w", encoding="utf-8") as f:
            f.write(runner_code)

        return bundle_dir, runner_path

    def build_standalone_bundle(self, output_dir="dist", clean_app_name="MST_Uygulamasi"):
        bundle_dir, _ = self._prepare_bundle_files(output_dir, clean_app_name)

        sh_lines = ["#!/bin/bash\n", 'cd "$(dirname "$0")"\n', "python3 runner.py\n"]
        sh_path = os.path.join(bundle_dir, "start.sh")
        with open(sh_path, "w", encoding="utf-8") as f:
            f.writelines(sh_lines)
        os.chmod(sh_path, 0o755)

        return bundle_dir

    def build_native_executable(self, output_dir="dist", clean_app_name="MST_Uygulamasi"):
        """PyInstaller kullanarak Python bağımsız gömülü tek binary (Binary Executable) derler."""
        bundle_dir, runner_path = self._prepare_bundle_files(output_dir, clean_app_name)

        add_data_mst = f"{os.path.join(bundle_dir, 'app_data.mst')}:."
        add_data_db = f"{os.path.join(bundle_dir, 'app_database.db')}:."
        add_data_manifest = f"{os.path.join(bundle_dir, 'manifest.json')}:."

        cmd = [
            "pyinstaller",
            "--noconsole",
            "--onefile",
            "--name", clean_app_name,
            "--distpath", bundle_dir,
            "--workpath", os.path.join(bundle_dir, "build"),
            "--specpath", bundle_dir,
            "--add-data", add_data_mst,
            "--add-data", add_data_db,
            "--add-data", add_data_manifest,
            runner_path
        ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"PyInstaller Derleme Hatası:\n{res.stderr}")

        build_path = os.path.join(bundle_dir, "build")
        spec_path = os.path.join(bundle_dir, f"{clean_app_name}.spec")
        if os.path.exists(build_path):
            shutil.rmtree(build_path)
        if os.path.exists(spec_path):
            os.remove(spec_path)

        return bundle_dir

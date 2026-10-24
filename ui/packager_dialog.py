#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class MSTPackagerDialog(tk.Toplevel):
    """MS Access Mimarisi 4. Faz: Standalone App Exe & Bundle Packager Engine"""

    def __init__(self, parent, project_engine, db_engine):
        super().__init__(parent)
        self.project_engine = project_engine
        self.db_engine = db_engine

        self.title("📦 MST Studio - Bağımsız Uygulama Paketleyici (Exe/Bundle)")
        self.geometry("540x420")
        self.resizable(False, False)

        self.setup_ui()

    def setup_ui(self):
        container = ttk.Frame(self, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="🚀 Bağımsız Uygulama Derleme Sihirbazı", font=("Helvetica", 11, "bold")).pack(anchor=tk.W, pady=(0, 10))
        ttk.Label(container, text="Tasarladığınız Low-Code uygulamasını, başka hiçbir bağımlılık gerektirmeden çalışacak bağımsız bir masaüstü yazılımına dönüştürün.", wraplength=500).pack(anchor=tk.W, pady=(0, 15))

        # Ayarlar Çerçevesi
        cfg_frame = ttk.LabelFrame(container, text=" Derleme Ayarları ", padding=10)
        cfg_frame.pack(fill=tk.X, pady=5)

        ttk.Label(cfg_frame, text="Uygulama Adı:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.e_app_name = ttk.Entry(cfg_frame, width=30)
        self.e_app_name.insert(0, self.project_engine.project_name or "Musteri_Yonetim_Sistemi")
        self.e_app_name.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(cfg_frame, text="Çıktı Formatı:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.cb_format = ttk.Combobox(cfg_frame, values=["Standalone Executable (Tek Dosya Binary/Exe)", "Portable Directory Bundle (Klasör Paketi)"], state="readonly", width=35)
        self.cb_format.current(0)
        self.cb_format.grid(row=1, column=1, padx=5, pady=4)

        self.var_embed_db = tk.BooleanVar(value=True)
        ttk.Checkbutton(cfg_frame, text="Mevcut SQLite Veritabanını Pakete Göm (.db)", variable=self.var_embed_db).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=6)

        # Durum Çubuğu
        self.lbl_status = ttk.Label(container, text="Hazır. Derleme için 'Paketle' butonuna basın.", font=("Helvetica", 9, "italic"), foreground="#555555")
        self.lbl_status.pack(anchor=tk.W, pady=10)

        # İlerleme Çubuğu
        self.progress = ttk.Progressbar(container, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=5)

        # Butonlar
        btn_frame = ttk.Frame(container)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        ttk.Button(btn_frame, text="⚙️ PyInstaller Bağımlılığını Kontrol Et", command=self.check_pyinstaller).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="🚀 Uygulamayı Paketle / Derle", command=self.build_package).pack(side=tk.RIGHT)

    def check_pyinstaller(self):
        pyinst_path = shutil.which("pyinstaller")
        if pyinst_path:
            messagebox.showinfo("MST Studio", f"✅ PyInstaller bulundu:\n{pyinst_path}")
        else:
            messagebox.showwarning("Uyarı", "⚠️ Sistemde PyInstaller bulunamadı!\nDerleme yapabilmek için terminalde 'pip install pyinstaller' çalıştırın.")

    def build_package(self):
        app_name = self.e_app_name.get().strip().replace(" ", "_")
        if not app_name:
            messagebox.showwarning("Uyarı", "Lütfen bir uygulama adı girin!")
            return

        out_dir = filedialog.askdirectory(title="Paketin Kaydedileceği Klasörü Seçin")
        if not out_dir:
            return

        self.lbl_status.config(text="⚙️ Derleme başlatılıyor, lütfen bekleyin...")
        self.progress.start(10)
        self.update_idletasks()

        try:
            # 1. Geçici Derleme Klasörü
            build_temp = os.path.join(out_dir, f"{app_name}_BuildTemp")
            if os.path.exists(build_temp):
                shutil.rmtree(build_temp)
            os.makedirs(build_temp, exist_ok=True)

            # 2. Proje Dosyasını ve DB'yi Geçici Klasöre Kaydet
            mst_file = os.path.join(build_temp, "app_data.mst")
            self.project_engine.save_project(mst_file)

            if self.var_embed_db.get() and os.path.exists(self.db_engine.db_path):
                shutil.copy(self.db_engine.db_path, os.path.join(build_temp, "mst_database.db"))

            # 3. Başlatıcı Python Betiği Oluştur
            entry_script = os.path.join(build_temp, "entry_point.py")
            with open(entry_script, "w", encoding="utf-8") as f:
                f.write('''import os, sys, tkinter as tk
from preview.live_simulator import LiveSimulator
from core.db_engine import DatabaseEngine
from core.project_engine import MSTProjectEngine
from core.i18n_engine import i18n

if __name__ == "__main__":
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    mst_path = os.path.join(base_dir, "app_data.mst")
    db_path = os.path.join(base_dir, "mst_database.db")

    engine = MSTProjectEngine("Runtime")
    engine.load_project(mst_path)
    db = DatabaseEngine(db_path)

    root = tk.Tk()
    root.withdraw()
    sim = LiveSimulator(root, db, i18n, engine.pages, engine.page_components, list(engine.pages.keys())[0])
    sim.protocol("WM_DELETE_WINDOW", sys.exit)
    root.mainloop()
''')

            # 4. PyInstaller Derlemesi
            pyinst_bin = shutil.which("pyinstaller") or "pyinstaller"
            cmd = [
                pyinst_bin,
                "--noconfirm",
                "--onedir" if "Bundle" in self.cb_format.get() else "--onefile",
                "--windowed",
                f"--name={app_name}",
                f"--add-data={mst_file}:.",
                f"--distpath={out_dir}",
                f"--workpath={os.path.join(build_temp, 'build')}",
                f"--specpath={build_temp}",
                entry_script
            ]

            if self.var_embed_db.get() and os.path.exists(self.db_engine.db_path):
                cmd.append(f"--add-data={os.path.join(build_temp, 'mst_database.db')}:.")

            res = subprocess.run(cmd, capture_output=True, text=True)

            self.progress.stop()
            if res.returncode == 0:
                self.lbl_status.config(text="🎉 Derleme başarıyla tamamlandı!")
                messagebox.showinfo("Başarılı", f"🎉 Uygulamanız başarıyla derlendi!\n\nÇıktı Adresi:\n{out_dir}")
                self.destroy()
            else:
                self.lbl_status.config(text="❌ Derleme hatası oluştu.")
                messagebox.showerror("Derleme Hatası", f"PyInstaller çıktısı:\n{res.stderr[:500]}")

        except Exception as e:
            self.progress.stop()
            self.lbl_status.config(text="❌ Hata oluştu.")
            messagebox.showerror("Hata", str(e))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.packager_engine import MSTPackagerEngine

class MSTPackagerDialog(tk.Toplevel):
    def __init__(self, parent, project_engine, db_engine):
        super().__init__(parent)
        self.project_engine = project_engine
        self.db_engine = db_engine
        self.packager = MSTPackagerEngine(project_engine, db_engine)

        self.title("MST Studio - Bağımsız Uygulama Paketleme Sihirbazı")
        self.geometry("480x420")
        self.resizable(False, False)

        self.setup_ui()

    def setup_ui(self):
        container = ttk.Frame(self, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="⚡ Bağımsız Masaüstü Uygulaması Derle & Paketle", font=("Helvetica", 11, "bold")).pack(pady=5)

        ttk.Label(container, text="Uygulama Adı:").pack(anchor=tk.W, pady=(8, 2))
        self.e_app_name = ttk.Entry(container, width=40)
        default_name = self.project_engine.project_name or "Masaustu_Uygulamam"
        clean_default = os.path.basename(default_name.rstrip("/\\"))
        self.e_app_name.insert(0, clean_default)
        self.e_app_name.pack(fill=tk.X, pady=2)

        ttk.Label(container, text="Paketleme Türü:").pack(anchor=tk.W, pady=(8, 2))
        self.cb_pkg_type = ttk.Combobox(
            container, 
            values=["Gömülü İkili Kod (Native Executable - PyInstaller)", "Taşınabilir Betik Demeti (Portable Script Bundle)"],
            state="readonly"
        )
        self.cb_pkg_type.current(0)
        self.cb_pkg_type.pack(fill=tk.X, pady=2)

        ttk.Label(container, text="Hedef Çıktı Dizini:").pack(anchor=tk.W, pady=(8, 2))
        path_frame = ttk.Frame(container)
        path_frame.pack(fill=tk.X, pady=2)

        default_dist = os.path.join(os.getcwd(), "dist")
        self.e_output_dir = ttk.Entry(path_frame)
        self.e_output_dir.insert(0, default_dist)
        self.e_output_dir.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(path_frame, text="Gözat...", command=self.browse_output_dir).pack(side=tk.RIGHT)

        ttk.Button(container, text="🚀 Derlemeyi ve Paketlemeyi Başlat", command=self.start_packaging).pack(pady=20)

    def browse_output_dir(self):
        d = filedialog.askdirectory(title="Hedef Çıktı Dizinini Seçin")
        if d:
            self.e_output_dir.delete(0, tk.END)
            self.e_output_dir.insert(0, d)

    def start_packaging(self):
        app_name = self.e_app_name.get().strip()
        out_dir = self.e_output_dir.get().strip()
        selected_type = "binary" if "Native" in self.cb_pkg_type.get() else "bundle"

        if not app_name:
            messagebox.showwarning("Eksik Bilgi", "Lütfen bir uygulama adı girin!")
            return

        try:
            bundle_path = self.packager.build_package(
                app_name=app_name, 
                package_type=selected_type, 
                output_dir=out_dir
            )
            
            msg = f"🎉 Bağımsız uygulamanız başarıyla derlendi!\n\nKlasör:\n{bundle_path}\n\n"
            if selected_type == "binary":
                msg += "Uygulama Python'dan bağımsız tek bir ikili dosya (Binary Executable) olarak üretilmiştir. Doğrudan çift tıklayarak çalıştırabilirsiniz!"
            else:
                msg += "Çalıştırmak için klasör içindeki 'start.sh' dosyasına çift tıklayabilirsiniz."

            messagebox.showinfo("Derleme Başarılı!", msg)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Derleme Hatası", str(e))

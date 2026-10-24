#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

class AutoPushGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 MST Studio - GitHub Otomatik Yayınlayıcı")
        self.root.geometry("420x300")
        self.root.resizable(False, False)

        self.setup_ui()

    def setup_ui(self):
        container = ttk.Frame(self.root, padding=20)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="🐙 GitHub Otomatik Sürüm Gönderici", font=("Helvetica", 11, "bold")).pack(pady=(0, 10))

        ttk.Label(container, text="Değişiklik Mesajı:").pack(anchor=tk.W, pady=(5, 2))
        self.e_msg = ttk.Entry(container, width=45)
        self.e_msg.insert(0, "Güncellemeler ve iyileştirmeler uygulandı")
        self.e_msg.pack(fill=tk.X, pady=2)

        ttk.Label(container, text="Sürüm Artış Türü:").pack(anchor=tk.W, pady=(10, 2))
        self.cb_type = ttk.Combobox(
            container, 
            values=["1) Yama / Düzeltme (Patch -> 1.0.1)", "2) Genel Özellik (Minor -> 1.1.0)", "3) Köklü Değişiklik (Major -> 2.0.0)", "4) Sürümü Artırma"],
            state="readonly"
        )
        self.cb_type.current(0)
        self.cb_type.pack(fill=tk.X, pady=2)

        btn = ttk.Button(container, text="🚀 GitHub'a Temiz Şekilde Gönder", command=self.run_push)
        btn.pack(pady=20)

    def run_push(self):
        choice_map = {0: "1", 1: "2", 2: "3", 3: "4"}
        choice = choice_map[self.cb_type.current()]
        msg = self.e_msg.get().strip()

        # release.sh dosyasını çağır
        cmd = f'echo "{choice}\n{msg}\n" | ./release.sh'
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                messagebox.showinfo("Başarılı!", f"🎉 Değişiklikler GitHub'a gönderildi!\n\nÇıktı:\n{res.stdout[-300:]}")
                self.root.destroy()
            else:
                messagebox.showerror("Hata", f"Gönderim hatası:\n{res.stderr}")
        except Exception as e:
            messagebox.showerror("Hata", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoPushGUI(root)
    root.mainloop()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox

class MSTPropertySheet(ttk.LabelFrame):
    def __init__(self, parent, db_engine, i18n_engine, on_update_cb=None, **kwargs):
        super().__init__(parent, text="⚙️ MST Özellikler Paneli", padding=10, **kwargs)
        self.db = db_engine
        self.i18n = i18n_engine
        self.on_update_cb = on_update_cb

        self.current_component = None
        self.current_page_name = None
        self.pages_dict = None

        self.setup_ui()

    def setup_ui(self):
        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def load_page_properties(self, page_name, pages_dict):
        self.clear_container()
        self.current_component = None
        self.current_page_name = page_name
        self.pages_dict = pages_dict

        p_info = pages_dict.get(page_name, {})

        ttk.Label(self.container, text=f"⚙️ Form Genel Ayarları: [{page_name}]", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(self.container, text="Gerekli Erişim Yetkisi (Rol):").pack(anchor=tk.W, pady=(5, 2))
        self.cb_role = ttk.Combobox(self.container, values=["Herkes", "Yönetici", "Kullanıcı", "Misafir"], state="readonly")
        self.cb_role.set(p_info.get("role", "Herkes"))
        self.cb_role.pack(fill=tk.X, pady=2)

        self.var_login = tk.BooleanVar(value=p_info.get("is_login", False))
        ttk.Checkbutton(self.container, text="🔑 Bu Form Kullanıcı Giriş Sayfasıdır", variable=self.var_login).pack(anchor=tk.W, pady=10)

        ttk.Button(self.container, text="💾 Form Ayarlarını Kaydet", command=self.save_page_properties).pack(pady=15)

    def save_page_properties(self):
        if self.current_page_name and self.pages_dict:
            self.pages_dict[self.current_page_name]["role"] = self.cb_role.get()
            self.pages_dict[self.current_page_name]["is_login"] = self.var_login.get()
            messagebox.showinfo("MST Studio", "Form genel ayarları kaydedildi!")

    def load_component(self, comp):
        self.clear_container()
        self.current_component = comp
        if not comp: return

        ttk.Label(self.container, text=f"📐 Denetim Özellikleri: [{comp['type']}]", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # 1. Konum ve Boyut Ayarları
        geom_frame = ttk.LabelFrame(self.container, text=" Konum & Boyut (Piksel) ", padding=5)
        geom_frame.pack(fill=tk.X, pady=5)

        g_grid = ttk.Frame(geom_frame)
        g_grid.pack(fill=tk.X)

        ttk.Label(g_grid, text="X:").grid(row=0, column=0, padx=2)
        self.e_x = ttk.Entry(g_grid, width=6)
        self.e_x.insert(0, str(comp['x']))
        self.e_x.grid(row=0, column=1, padx=4)

        ttk.Label(g_grid, text="Y:").grid(row=0, column=2, padx=2)
        self.e_y = ttk.Entry(g_grid, width=6)
        self.e_y.insert(0, str(comp['y']))
        self.e_y.grid(row=0, column=3, padx=4)

        ttk.Label(g_grid, text="En:").grid(row=1, column=0, padx=2, pady=4)
        self.e_w = ttk.Entry(g_grid, width=6)
        self.e_w.insert(0, str(comp['w']))
        self.e_w.grid(row=1, column=1, padx=4, pady=4)

        ttk.Label(g_grid, text="Boy:").grid(row=1, column=2, padx=2, pady=4)
        self.e_h = ttk.Entry(g_grid, width=6)
        self.e_h.insert(0, str(comp['h']))
        self.e_h.grid(row=1, column=3, padx=4, pady=4)

        # 2. Metin / Başlık
        ttk.Label(self.container, text="Arayüz Başlığı / Etiket:").pack(anchor=tk.W, pady=(8, 2))
        self.e_text = ttk.Entry(self.container)
        self.e_text.insert(0, comp.get("text", ""))
        self.e_text.pack(fill=tk.X, pady=2)

        # 3. Veritabanı Bağlantısı
        ttk.Label(self.container, text="Hedef Veri Tablosu:").pack(anchor=tk.W, pady=(8, 2))
        tables = self.db.get_tables()
        self.cb_table = ttk.Combobox(self.container, values=[""] + tables, state="readonly")
        self.cb_table.set(comp.get("table", ""))
        self.cb_table.pack(fill=tk.X, pady=2)

        ttk.Label(self.container, text="Bağlı Sütun / Alan:").pack(anchor=tk.W, pady=(8, 2))
        self.cb_field = ttk.Combobox(self.container, state="readonly")
        self.cb_field.pack(fill=tk.X, pady=2)

        def update_fields(event=None):
            tbl = self.cb_table.get()
            if tbl:
                cols = [c["name"] for c in self.db.get_table_columns(tbl)]
                self.cb_field["values"] = [""] + cols
            else:
                self.cb_field["values"] = []

        self.cb_table.bind("<<ComboboxSelected>>", update_fields)
        update_fields()
        self.cb_field.set(comp.get("field", ""))

        ttk.Button(self.container, text="💾 Özellikleri Kaydet", command=self.save_component_properties).pack(pady=15)

    def save_component_properties(self):
        if self.current_component:
            try:
                self.current_component["x"] = int(self.e_x.get())
                self.current_component["y"] = int(self.e_y.get())
                self.current_component["w"] = int(self.e_w.get())
                self.current_component["h"] = int(self.e_h.get())
            except ValueError:
                pass

            self.current_component["text"] = self.e_text.get().strip()
            self.current_component["table"] = self.cb_table.get()
            self.current_component["field"] = self.cb_field.get()

            if self.on_update_cb:
                self.on_update_cb()
            messagebox.showinfo("MST Studio", "Denetim özellikleri güncellendi!")

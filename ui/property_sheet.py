#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox

class MSTPropertySheet(ttk.LabelFrame):
    """MS Access Mimarisi 1. Faz: Sekmeli Özellikler Paneli (Düzeltilmiş Düzen)"""

    def __init__(self, parent, db_engine, i18n_engine, on_update_cb=None, **kwargs):
        super().__init__(parent, text="⚙️ MST Özellikler Paneli (Access Style)", padding=5, **kwargs)
        self.db = db_engine
        self.i18n = i18n_engine
        self.on_update_cb = on_update_cb

        self.current_component = None
        self.current_page_name = None
        self.pages_dict = None

        self.setup_ui()

    def setup_ui(self):
        # Üst Kısım: 4 Ana Sekme
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_format = ttk.Frame(self.notebook, padding=8)
        self.tab_data = ttk.Frame(self.notebook, padding=8)
        self.tab_events = ttk.Frame(self.notebook, padding=8)
        self.tab_other = ttk.Frame(self.notebook, padding=8)

        self.notebook.add(self.tab_format, text="🎨 Biçim")
        self.notebook.add(self.tab_data, text="💾 Veri")
        self.notebook.add(self.tab_events, text="⚡ Olaylar")
        self.notebook.add(self.tab_other, text="⚙️ Diğer")

        # Alt Kısım: Sadece TEK BİR Kaydet Butonu
        self.btn_save = ttk.Button(self, text="💾 Özellikleri Kaydet", command=self.save_properties)
        self.btn_save.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

    def clear_all_tabs(self):
        for tab in [self.tab_format, self.tab_data, self.tab_events, self.tab_other]:
            for widget in tab.winfo_children():
                widget.destroy()

    def load_page_properties(self, page_name, pages_dict):
        """Form seviyesi genel ayarlar."""
        self.clear_all_tabs()
        self.current_component = None
        self.current_page_name = page_name
        self.pages_dict = pages_dict

        p_info = pages_dict.get(page_name, {})

        # Biçim Sekmesi
        ttk.Label(self.tab_format, text=f"📋 Form Başlığı: {page_name}", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))

        # Veri Sekmesi
        ttk.Label(self.tab_data, text="Gerekli Erişim Yetkisi (Rol):").pack(anchor=tk.W, pady=(5, 2))
        self.cb_role = ttk.Combobox(self.tab_data, values=["Herkes", "Yönetici", "Kullanıcı", "Misafir"], state="readonly")
        self.cb_role.set(p_info.get("role", "Herkes"))
        self.cb_role.pack(fill=tk.X, pady=2)

        self.var_login = tk.BooleanVar(value=p_info.get("is_login", False))
        ttk.Checkbutton(self.tab_data, text="🔑 Bu Form Kullanıcı Giriş Sayfasıdır", variable=self.var_login).pack(anchor=tk.W, pady=10)

    def load_component(self, comp):
        """Denetim özellikleri dolduruluyor."""
        self.clear_all_tabs()
        self.current_component = comp
        if not comp: return

        # 1. BİÇİM (FORMAT) SEKMESİ
        geom_frame = ttk.LabelFrame(self.tab_format, text=" Konum & Boyut (Piksel) ", padding=5)
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

        ttk.Label(self.tab_format, text="Arayüz Başlığı / Etiket:").pack(anchor=tk.W, pady=(8, 2))
        self.e_text = ttk.Entry(self.tab_format)
        self.e_text.insert(0, comp.get("text", ""))
        self.e_text.pack(fill=tk.X, pady=2)

        self.var_visible = tk.BooleanVar(value=comp.get("visible", True))
        ttk.Checkbutton(self.tab_format, text="👁️ Görünür (Visible)", variable=self.var_visible).pack(anchor=tk.W, pady=6)

        # 2. VERİ (DATA) SEKMESİ
        tables = self.db.get_tables()
        ttk.Label(self.tab_data, text="Hedef Veri Tablosu:").pack(anchor=tk.W, pady=(5, 2))
        self.cb_table = ttk.Combobox(self.tab_data, values=[""] + tables, state="readonly")
        self.cb_table.set(comp.get("table", ""))
        self.cb_table.pack(fill=tk.X, pady=2)

        if comp['type'] == "Alt Form (Master-Detail)":
            md_frame = ttk.LabelFrame(self.tab_data, text=" 🔗 Master-Detail Bağlantısı ", padding=5)
            md_frame.pack(fill=tk.X, pady=8)

            ttk.Label(md_frame, text="Ana Form Alanı (Master):").pack(anchor=tk.W, pady=2)
            self.e_master_field = ttk.Entry(md_frame)
            self.e_master_field.insert(0, comp.get("master_field", "id"))
            self.e_master_field.pack(fill=tk.X, pady=2)

            ttk.Label(md_frame, text="Alt Tablo FK Alanı (Detail):").pack(anchor=tk.W, pady=2)
            self.cb_detail_field = ttk.Combobox(md_frame, state="readonly")
            self.cb_detail_field.pack(fill=tk.X, pady=2)

            def update_detail_fields(event=None):
                tbl = self.cb_table.get()
                if tbl:
                    cols = [c["name"] for c in self.db.get_table_columns(tbl)]
                    self.cb_detail_field["values"] = [""] + cols
                else:
                    self.cb_detail_field["values"] = []

            self.cb_table.bind("<<ComboboxSelected>>", update_detail_fields)
            update_detail_fields()
            self.cb_detail_field.set(comp.get("detail_field", ""))

        else:
            ttk.Label(self.tab_data, text="Bağlı Sütun / Alan:").pack(anchor=tk.W, pady=(8, 2))
            self.cb_field = ttk.Combobox(self.tab_data, state="readonly")
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

            ttk.Label(self.tab_data, text="Varsayılan Değer:").pack(anchor=tk.W, pady=(8, 2))
            self.e_default_val = ttk.Entry(self.tab_data)
            self.e_default_val.insert(0, comp.get("default_value", ""))
            self.e_default_val.pack(fill=tk.X, pady=2)

            self.var_required = tk.BooleanVar(value=comp.get("is_required", False))
            ttk.Checkbutton(self.tab_data, text="⚠️ Zorunlu Alan", variable=self.var_required).pack(anchor=tk.W, pady=6)

        # 3. OLAYLAR (EVENTS) SEKMESİ
        ttk.Label(self.tab_events, text="⚡ Tıklandığında (OnClick):").pack(anchor=tk.W, pady=(5, 2))
        actions = [
            "Kaydet / Güncelle (Save/Update)",
            "Yeni Kayıt Temizle (New Record)",
            "Seçili Kaydı Sil (Delete)",
            "Sonraki Kayda Git (Next)",
            "Önceki Kayda Git (Previous)",
            "Sayfaya Git (Navigate)",
            "Kullanıcı Girişi Yap"
        ]
        self.cb_action = ttk.Combobox(self.tab_events, values=[""] + actions, state="readonly")
        self.cb_action.set(comp.get("action", "Kaydet / Güncelle (Save/Update)" if comp['type'] == "Buton" else ""))
        self.cb_action.pack(fill=tk.X, pady=2)

        ttk.Label(self.tab_events, text="Hedef Form / Sayfa:").pack(anchor=tk.W, pady=(8, 2))
        pages_list = list(self.pages_dict.keys()) if self.pages_dict else []
        self.cb_target = ttk.Combobox(self.tab_events, values=[""] + pages_list, state="readonly")
        self.cb_target.set(comp.get("target", ""))
        self.cb_target.pack(fill=tk.X, pady=2)

        # 4. DİĞER (OTHER) SEKMESİ
        ttk.Label(self.tab_other, text="Denetim Adı (Name):").pack(anchor=tk.W, pady=(5, 2))
        self.e_name = ttk.Entry(self.tab_other)
        default_name = comp.get("name", f"{comp['type'].lower().replace(' ', '_')}_{comp['id']}")
        self.e_name.insert(0, default_name)
        self.e_name.pack(fill=tk.X, pady=2)

        ttk.Label(self.tab_other, text="Tab Sırası (TabIndex):").pack(anchor=tk.W, pady=(8, 2))
        self.e_tab_index = ttk.Entry(self.tab_other)
        self.e_tab_index.insert(0, str(comp.get("tab_index", comp['id'])))
        self.e_tab_index.pack(fill=tk.X, pady=2)

        ttk.Label(self.tab_other, text="İpucu Metni (Tooltip):").pack(anchor=tk.W, pady=(8, 2))
        self.e_tooltip = ttk.Entry(self.tab_other)
        self.e_tooltip.insert(0, comp.get("tooltip", ""))
        self.e_tooltip.pack(fill=tk.X, pady=2)

    def save_properties(self):
        if self.current_component:
            try:
                self.current_component["x"] = int(self.e_x.get())
                self.current_component["y"] = int(self.e_y.get())
                self.current_component["w"] = int(self.e_w.get())
                self.current_component["h"] = int(self.e_h.get())
            except (ValueError, AttributeError):
                pass

            if hasattr(self, 'e_text'):
                self.current_component["text"] = self.e_text.get().strip()
            if hasattr(self, 'var_visible'):
                self.current_component["visible"] = self.var_visible.get()

            if hasattr(self, 'cb_table'):
                self.current_component["table"] = self.cb_table.get()

            if self.current_component['type'] == "Alt Form (Master-Detail)":
                if hasattr(self, 'e_master_field'):
                    self.current_component["master_field"] = self.e_master_field.get().strip()
                if hasattr(self, 'cb_detail_field'):
                    self.current_component["detail_field"] = self.cb_detail_field.get()
            else:
                if hasattr(self, 'cb_field'):
                    self.current_component["field"] = self.cb_field.get()
                if hasattr(self, 'e_default_val'):
                    self.current_component["default_value"] = self.e_default_val.get().strip()
                if hasattr(self, 'var_required'):
                    self.current_component["is_required"] = self.var_required.get()

            if hasattr(self, 'cb_action'):
                self.current_component["action"] = self.cb_action.get()
            if hasattr(self, 'cb_target'):
                self.current_component["target"] = self.cb_target.get()

            if hasattr(self, 'e_name'):
                self.current_component["name"] = self.e_name.get().strip()
            if hasattr(self, 'e_tab_index'):
                try:
                    self.current_component["tab_index"] = int(self.e_tab_index.get())
                except ValueError:
                    pass
            if hasattr(self, 'e_tooltip'):
                self.current_component["tooltip"] = self.e_tooltip.get().strip()

            if self.on_update_cb:
                self.on_update_cb()
            messagebox.showinfo("MST Studio", "Özellikler başarıyla kaydedildi!")

        elif self.current_page_name and self.pages_dict:
            if hasattr(self, 'cb_role'):
                self.pages_dict[self.current_page_name]["role"] = self.cb_role.get()
            if hasattr(self, 'var_login'):
                self.pages_dict[self.current_page_name]["is_login"] = self.var_login.get()
            messagebox.showinfo("MST Studio", "Form genel ayarları kaydedildi!")

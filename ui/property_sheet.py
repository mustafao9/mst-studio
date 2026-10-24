#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox

class MSTPropertySheet(ttk.LabelFrame):
    def __init__(self, parent, db_engine, i18n_engine, on_update_cb, **kwargs):
        super().__init__(parent, text=" ⚙️ MST Özellikler Paneli ", padding=10, **kwargs)
        self.db = db_engine
        self.i18n = i18n_engine
        self.on_update_cb = on_update_cb
        self.current_comp = None
        self.active_page_ref = None
        self.pages_dict_ref = None

        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

    def load_page_properties(self, page_name, pages_dict):
        """Hiçbir bileşen seçili değilken Form ve Proje Genel Ayarlarını gösterir."""
        self.current_comp = None
        self.active_page_ref = page_name
        self.pages_dict_ref = pages_dict
        
        for w in self.container.winfo_children():
            w.destroy()

        page_info = pages_dict.get(page_name, {})

        ttk.Label(self.container, text=f"📋 Form Genel Ayarları: [{page_name}]", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=5)
        ttk.Separator(self.container, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        ttk.Label(self.container, text="Gerekli Erişim Yetkisi (Rol):").pack(anchor=tk.W, pady=2)
        cb_role = ttk.Combobox(self.container, values=["Herkes", "Admin", "Kasiyer"], state="readonly")
        cb_role.set(page_info.get("role", "Herkes"))
        cb_role.pack(fill=tk.X, pady=2)

        chk_login_var = tk.BooleanVar(value=page_info.get("is_login", False))
        ttk.Checkbutton(self.container, text="🔑 Bu Form Kullanıcı Giriş Sayfasıdır", variable=chk_login_var).pack(anchor=tk.W, pady=8)

        def save_page_props():
            page_info["role"] = cb_role.get()
            page_info["is_login"] = chk_login_var.get()
            messagebox.showinfo("MST Studio", f"'{page_name}' form ayarları güncellendi!")
            if self.on_update_cb:
                self.on_update_cb()

        ttk.Button(self.container, text="💾 Form Ayarlarını Kaydet", command=save_page_props).pack(pady=15, fill=tk.X)

    def load_component(self, comp):
        """Seçili bileşenin görünüm, veri ve doğrulama parametrelerini yükler."""
        self.current_comp = comp
        for w in self.container.winfo_children():
            w.destroy()

        if not comp:
            return

        ttk.Label(self.container, text=f"⚙️ Denetim Özellikleri: [{comp['type']}]", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=5)
        ttk.Separator(self.container, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        # 1. GENEL / GÖRÜNÜM
        ttk.Label(self.container, text="Arayüz Başlığı / Etiket:").pack(anchor=tk.W, pady=2)
        e_text = ttk.Entry(self.container)
        e_text.insert(0, comp.get('text', ''))
        e_text.pack(fill=tk.X, pady=2)

        tables = self.db.get_tables()

        # 2. VERİ BAĞLANTISI
        if comp['type'] in ["Metin Kutusu", "Açılır Liste", "Onay Kutusu", "Veri Tablosu"]:
            ttk.Label(self.container, text="Hedef Veri Tablosu:").pack(anchor=tk.W, pady=2)
            cb_table = ttk.Combobox(self.container, values=tables)
            cb_table.set(comp.get('table', ''))
            cb_table.pack(fill=tk.X, pady=2)

            ttk.Label(self.container, text="Bağlı Sütun / Alan:").pack(anchor=tk.W, pady=2)
            cb_field = ttk.Combobox(self.container, values=["ad_soyad", "kullanici_adi", "sifre", "rol", "urun_adi", "fiyati", "stok", "sehir"])
            cb_field.set(comp.get('field', ''))
            cb_field.pack(fill=tk.X, pady=2)

        if comp['type'] == "Açılır Liste":
            ttk.Label(self.container, text="--- Açılır Liste Veri Kaynağı ---", font=("Helvetica", 9, "bold")).pack(anchor=tk.W, pady=6)
            ttk.Label(self.container, text="Lookup Tablo:").pack(anchor=tk.W, pady=1)
            cb_lookup_tbl = ttk.Combobox(self.container, values=tables)
            cb_lookup_tbl.set(comp.get('lookup_table', ''))
            cb_lookup_tbl.pack(fill=tk.X, pady=1)

            ttk.Label(self.container, text="Lookup Sütun:").pack(anchor=tk.W, pady=1)
            cb_lookup_fld = ttk.Combobox(self.container, values=["ad_soyad", "urun_adi", "sehir", "rol"])
            cb_lookup_fld.set(comp.get('lookup_field', ''))
            cb_lookup_fld.pack(fill=tk.X, pady=1)

            ttk.Label(self.container, text="Manuel Seçenekler (Virgülle):").pack(anchor=tk.W, pady=1)
            e_options = ttk.Entry(self.container)
            e_options.insert(0, comp.get('options', ''))
            e_options.pack(fill=tk.X, pady=1)

        elif comp['type'] == "Buton":
            ttk.Label(self.container, text="Buton Eylemi (Action Wizard):").pack(anchor=tk.W, pady=2)
            cb_action = ttk.Combobox(self.container, values=["Kullanıcı Girişi Yap", "Kayıt Ekle", "Sayfaya Git", "Kapat"])
            cb_action.set(comp.get('action', ''))
            cb_action.pack(fill=tk.X, pady=2)

            ttk.Label(self.container, text="Hedef Sayfa:").pack(anchor=tk.W, pady=2)
            cb_target = ttk.Combobox(self.container, values=["Giris_Sayfasi", "Ana_Sayfa", "Musteri_Yonetimi"])
            cb_target.set(comp.get('target', ''))
            cb_target.pack(fill=tk.X, pady=2)

        # 3. VERİ DOĞRULAMA (VALIDATION RULES)
        if comp['type'] in ["Metin Kutusu", "Açılır Liste"]:
            ttk.Label(self.container, text="--- Veri Doğrulama (Validation) ---", font=("Helvetica", 9, "bold")).pack(anchor=tk.W, pady=6)
            
            chk_req_var = tk.BooleanVar(value=comp.get("is_required", False))
            ttk.Checkbutton(self.container, text="Zorunlu Alan (Boş Geçilemez)", variable=chk_req_var).pack(anchor=tk.W, pady=2)

            ttk.Label(self.container, text="Doğrulama Tipi:").pack(anchor=tk.W, pady=1)
            cb_val_rule = ttk.Combobox(self.container, values=["Yok", "E-Posta", "Telefon", "Sayısal"], state="readonly")
            cb_val_rule.set(comp.get("validation_rule", "Yok"))
            cb_val_rule.pack(fill=tk.X, pady=1)

            ttk.Label(self.container, text="Hata Mesajı:").pack(anchor=tk.W, pady=1)
            e_val_msg = ttk.Entry(self.container)
            e_val_msg.insert(0, comp.get("validation_msg", "Bu alanın doldurulması zorunludur!"))
            e_val_msg.pack(fill=tk.X, pady=1)

        def save():
            comp['text'] = e_text.get().strip()
            if comp['type'] in ["Metin Kutusu", "Açılır Liste", "Onay Kutusu", "Veri Tablosu"]:
                comp['table'] = cb_table.get().strip()
                comp['field'] = cb_field.get().strip()
            if comp['type'] == "Açılır Liste":
                comp['lookup_table'] = cb_lookup_tbl.get().strip()
                comp['lookup_field'] = cb_lookup_fld.get().strip()
                comp['options'] = e_options.get().strip()
            elif comp['type'] == "Buton":
                comp['action'] = cb_action.get().strip()
                comp['target'] = cb_target.get().strip()

            if comp['type'] in ["Metin Kutusu", "Açılır Liste"]:
                comp['is_required'] = chk_req_var.get()
                comp['validation_rule'] = cb_val_rule.get()
                comp['validation_msg'] = e_val_msg.get().strip()

            if self.on_update_cb:
                self.on_update_cb()

        ttk.Button(self.container, text="💾 Özellikleri Kaydet", command=save).pack(pady=12, fill=tk.X)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
from core.query_builder import MSTQueryBuilder

class MSTQueryBuilderDialog(tk.Toplevel):
    def __init__(self, parent, db_engine, on_save_cb=None):
        super().__init__(parent)
        self.db = db_engine
        self.on_save_cb = on_save_cb

        self.title("🔍 MST Studio - Görsel SQL & JOIN Sorgu Sihirbazı")
        self.geometry("720x540")

        self.tables = self.db.get_tables()
        self.query_builder = None

        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self, text="⚡ Görsel İlişkisel Sorgu (SQL View) Oluşturucu", font=("Helvetica", 11, "bold")).pack(pady=10)
        
        container = ttk.Frame(self, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        # Ana Tablo Seçimi
        top_frame = ttk.Frame(container)
        top_frame.pack(fill=tk.X, pady=5)

        ttk.Label(top_frame, text="Ana Tablo:").pack(side=tk.LEFT, padx=5)
        self.cb_main_tbl = ttk.Combobox(top_frame, values=self.tables, state="readonly", width=20)
        if self.tables:
            self.cb_main_tbl.current(0)
        self.cb_main_tbl.pack(side=tk.LEFT, padx=5)

        # JOIN İlişkisi
        join_frame = ttk.LabelFrame(container, text=" Tablo İlişkisi (JOIN) ", padding=10)
        join_frame.pack(fill=tk.X, pady=10)

        ttk.Label(join_frame, text="İlişki Tipi:").grid(row=0, column=0, padx=5, pady=2)
        self.cb_join_type = ttk.Combobox(join_frame, values=["INNER JOIN", "LEFT JOIN"], state="readonly", width=12)
        self.cb_join_type.current(0)
        self.cb_join_type.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(join_frame, text="Hedef Tablo:").grid(row=0, column=2, padx=5, pady=2)
        self.cb_ref_tbl = ttk.Combobox(join_frame, values=self.tables, state="readonly", width=18)
        self.cb_ref_tbl.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(join_frame, text="Kaynak Sütun:").grid(row=1, column=0, padx=5, pady=2)
        self.e_left_col = ttk.Entry(join_frame, width=15)
        self.e_left_col.insert(0, "sehir_id")
        self.e_left_col.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(join_frame, text="Hedef Sütun:").grid(row=1, column=2, padx=5, pady=2)
        self.e_right_col = ttk.Entry(join_frame, width=15)
        self.e_right_col.insert(0, "id")
        self.e_right_col.grid(row=1, column=3, padx=5, pady=2)

        # SQL Ön İzleme
        ttk.Label(container, text="Üretilen SQL Sorgusu:").pack(anchor=tk.W, pady=2)
        self.txt_sql = tk.Text(container, height=6, font=("Consolas", 10))
        self.txt_sql.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_bar = ttk.Frame(self, padding=10)
        btn_bar.pack(fill=tk.X)

        ttk.Button(btn_bar, text="⚡ SQL Oluştur & Ön İzle", command=self.generate_sql).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_bar, text="💾 Sorguyu Görünüm Olarak Kaydet", command=self.save_query).pack(side=tk.RIGHT, padx=5)

    def generate_sql(self):
        main_tbl = self.cb_main_tbl.get()
        ref_tbl = self.cb_ref_tbl.get()
        j_type = self.cb_join_type.get().split()[0]
        l_col = self.e_left_col.get().strip()
        r_col = self.e_right_col.get().strip()

        if not main_tbl or not ref_tbl:
            messagebox.showwarning("Eksik Seçim", "Lütfen ana ve hedef tabloları seçin!")
            return

        builder = MSTQueryBuilder(main_tbl)
        builder.add_join(j_type, ref_tbl, f"{main_tbl}.{l_col}", f"{ref_tbl}.{r_col}")
        
        sql = builder.build_sql()
        self.txt_sql.delete("1.0", tk.END)
        self.txt_sql.insert(tk.END, sql)
        self.query_builder = builder

    def save_query(self):
        sql = self.txt_sql.get("1.0", tk.END).strip()
        if not sql:
            messagebox.showwarning("Uyarı", "Lütfen önce SQL sorgusunu oluşturun!")
            return

        if self.on_save_cb:
            self.on_save_cb(sql)
        messagebox.showinfo("Başarılı", "Sorgu başarıyla oluşturuldu ve kaydedildi!")
        self.destroy()

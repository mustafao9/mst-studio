#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox

class MSTDataEditor(tk.Toplevel):
    """MS Access Mimarisi 3. Faz: Datasheet View (In-Place Cell Editing & Totals Row)"""

    def __init__(self, parent, db_engine, table_name, on_change_cb=None):
        super().__init__(parent)
        self.db = db_engine
        self.table_name = table_name
        self.on_change_cb = on_change_cb

        self.title(f"📊 MST Datasheet View - [{self.table_name}]")
        self.geometry("900x560")

        self.columns = []
        self.primary_key = "id"

        self.setup_ui()
        self.setup_styles()
        self.load_data()

    def setup_styles(self):
        style = ttk.Style(self)
        style.configure(
            "Datasheet.Treeview",
            font=("Segoe UI", 9),
            rowheight=26,
            gridlines=True,
            background="#ffffff",
            fieldbackground="#ffffff"
        )
        style.configure(
            "Datasheet.Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background="#e1e6ed",
            foreground="#212529"
        )
        style.map("Datasheet.Treeview", background=[("selected", "#0078d4")], foreground=[("selected", "#ffffff")])

    def setup_ui(self):
        toolbar = ttk.Frame(self, padding=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(toolbar, text="➕ Yeni Satır Ekle", command=self.add_row).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="🗑️ Seçili Satırı Sil", command=self.delete_selected_row).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="🔄 Yenile", command=self.load_data).pack(side=tk.LEFT, padx=3)

        table_frame = ttk.Frame(self, padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(table_frame, style="Datasheet.Treeview", show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", self.on_double_click_cell)

        # Alt Toplamlar Çubuğu (Status Bar)
        self.status_bar = ttk.Frame(self, padding=4, relief="sunken")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.lbl_totals = ttk.Label(self.status_bar, text="Toplam Kayıt: 0", font=("Helvetica", 9, "bold"))
        self.lbl_totals.pack(side=tk.LEFT, padx=5)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        cols_info = self.db.get_table_columns(self.table_name)
        self.columns = [c["name"] for c in cols_info]
        
        for c in cols_info:
            if c["pk"]:
                self.primary_key = c["name"]
                break

        self.tree["columns"] = self.columns
        for col in self.columns:
            self.tree.heading(col, text=f"❖ {col.upper()}", anchor="center")
            self.tree.column(col, width=140, anchor="w", stretch=True)

        rows = self.db.get_table_data(self.table_name)
        
        self.tree.tag_configure("evenrow", background="#f9fbfd")
        self.tree.tag_configure("oddrow", background="#ffffff")

        for i, r in enumerate(rows):
            row_vals = [r.get(col, '') for col in self.columns]
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", tk.END, iid=str(r.get(self.primary_key, i+1)), values=row_vals, tags=(tag,))

        self.lbl_totals.config(text=f"📊 Toplam Kayıt Sayısı: {len(rows)}")

    def on_double_click_cell(self, event):
        """Çift tıklanan hücrede yerinde metin kutusu açar (In-Place Edit)."""
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell": return

        column_id = self.tree.identify_column(event.x)
        col_idx = int(column_id.replace("#", "")) - 1
        col_name = self.columns[col_idx]

        if col_name == self.primary_key:
            messagebox.showinfo("MST Studio", "Birincil Anahtar (ID) sütunu doğrudan değiştirilemez.")
            return

        item_id = self.tree.focus()
        if not item_id: return

        x, y, w, h = self.tree.bbox(item_id, column_id)
        current_val = self.tree.item(item_id, "values")[col_idx]

        entry = ttk.Entry(self.tree)
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, str(current_val))
        entry.focus()

        def save_edit(event=None):
            new_val = entry.get().strip()
            entry.destroy()
            if new_val != str(current_val):
                sql = f"UPDATE {self.db.sanitize(self.table_name)} SET {self.db.sanitize(col_name)} = ? WHERE {self.db.sanitize(self.primary_key)} = ?"
                try:
                    self.db.execute_query(sql, (new_val, item_id))
                    self.load_data()
                    if self.on_change_cb: self.on_change_cb()
                except Exception as e:
                    messagebox.showerror("Hata", f"Güncelleme yapılamadı:\n{str(e)}")

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", lambda e: entry.destroy())

    def add_row(self):
        non_pk_cols = [c for c in self.columns if c != self.primary_key]
        if not non_pk_cols: return

        cols_str = ", ".join([self.db.sanitize(c) for c in non_pk_cols])
        placeholders = ", ".join(["?" for _ in non_pk_cols])
        default_vals = ["(Yeni)" if i == 0 else "" for i in range(len(non_pk_cols))]

        sql = f"INSERT INTO {self.db.sanitize(self.table_name)} ({cols_str}) VALUES ({placeholders})"
        try:
            self.db.execute_query(sql, tuple(default_vals))
            self.load_data()
            if self.on_change_cb: self.on_change_cb()
        except Exception as e:
            messagebox.showerror("Hata", f"Yeni satır eklenemedi:\n{str(e)}")

    def delete_selected_row(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz satırı seçin!")
            return

        item_id = sel[0]
        if messagebox.askyesno("Onay", "Seçili satır kalıcı olarak silinecek. Emin misiniz?"):
            sql = f"DELETE FROM {self.db.sanitize(self.table_name)} WHERE {self.db.sanitize(self.primary_key)} = ?"
            try:
                self.db.execute_query(sql, (item_id,))
                self.load_data()
                if self.on_change_cb: self.on_change_cb()
            except Exception as e:
                messagebox.showerror("Hata", f"Satır silinemedi:\n{str(e)}")

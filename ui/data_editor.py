#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox

class MSTDataEditor(tk.Toplevel):
    """Access / Excel mantığında hücre içi doğrudan (In-Place) canlı düzenleme ve otomatik kaydetme penceresi."""

    def __init__(self, parent, db_engine, table_name, on_change_cb=None):
        super().__init__(parent)
        self.db = db_engine
        self.table_name = table_name
        self.on_change_cb = on_change_cb

        self.title(f"📊 MST Veri Editörü (Datasheet) - [{table_name}]")
        self.geometry("900x560")

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Üst Araç Çubuğu
        toolbar = ttk.Frame(self, padding=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(toolbar, text="➕ Yeni Satır Ekle", command=self.add_empty_row).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="🗑️ Seçili Satırı Sil", command=self.delete_selected_row).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="🔄 Yenile", command=self.load_data).pack(side=tk.LEFT, padx=3)
        
        lbl_hint = ttk.Label(toolbar, text="💡 İpucu: Hücreye çift tıklayarak veriyi doğrudan değiştirebilirsiniz.", font=("Helvetica", 9, "italic"))
        lbl_hint.pack(side=tk.RIGHT, padx=10)

        # Tablo Grid Alanı
        grid_frame = ttk.Frame(self, padding=5)
        grid_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(grid_frame, show="headings", selectmode="browse")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(grid_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self.on_double_click_cell)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            cols_info = self.db.get_table_columns(self.table_name)
            self.columns = [ci['name'] for ci in cols_info]
            
            self.tree["columns"] = self.columns
            for col in self.columns:
                self.tree.heading(col, text=f"🔹 {col.upper()}")
                self.tree.column(col, width=130, anchor="w")

            cursor = self.db.execute_query(f"SELECT * FROM {self.db.sanitize(self.table_name)}")
            for row in cursor.fetchall():
                self.tree.insert("", tk.END, values=row)

            # En alta varsayılan ekleme satırı koy
            empty_vals = ["* (Yeni)" if i == 0 else "" for i in range(len(self.columns))]
            self.tree.insert("", tk.END, values=empty_vals, tags=("new_row",))
            self.tree.tag_configure("new_row", foreground="#888888")

        except Exception as e:
            messagebox.showerror("Veri Yükleme Hatası", str(e))

    def on_double_click_cell(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if not item or not column:
            return

        col_idx = int(column.replace("#", "")) - 1
        col_name = self.columns[col_idx]

        if col_name.lower() == "id":
            messagebox.showinfo("Bilgi", "Birincil anahtar (ID) otomatik artan alandır, elle değiştirilemez.")
            return

        # Hücre Geometrisi Bulma
        bbox = self.tree.bbox(item, column)
        if not bbox:
            return

        x, y, w, h = bbox
        row_vals = list(self.tree.item(item)["values"])
        old_val = row_vals[col_idx] if col_idx < len(row_vals) else ""
        row_id = row_vals[0] if len(row_vals) > 0 else None

        # Akıllı İlişkili Tablo Tespiti (Örn: sehir_id veya sehir)
        lookup_options = None
        if "sehir" in col_name.lower() or "kategori" in col_name.lower() or "rol" in col_name.lower():
            for t in self.db.get_tables():
                if t in col_name.lower() or col_name.lower() in t:
                    try:
                        cols = [ci['name'] for ci in self.db.get_table_columns(t) if ci['name'].lower() != 'id']
                        if cols:
                            cur = self.db.execute_query(f"SELECT {self.db.sanitize(cols[0])} FROM {self.db.sanitize(t)}")
                            lookup_options = [str(r[0]) for r in cur.fetchall()]
                    except Exception:
                        pass

        # Satır İçi Düzenleyici (In-Place Widget Overlay)
        if lookup_options:
            editor = ttk.Combobox(self.tree, values=lookup_options, state="readonly")
            editor.set(str(old_val))
        else:
            editor = ttk.Entry(self.tree)
            editor.insert(0, str(old_val) if old_val != "* (Yeni)" else "")

        editor.place(x=x, y=y, width=w, height=h)
        editor.focus_set()

        def save_inline_value(event=None):
            new_val = editor.get().strip()
            editor.destroy()

            if new_val == str(old_val):
                return

            if str(row_id).startswith("*"):
                # YENİ SATIR EKLEME (INSERT)
                if new_val:
                    sql = f"INSERT INTO {self.db.sanitize(self.table_name)} ({self.db.sanitize(col_name)}) VALUES (?)"
                    try:
                        self.db.execute_query(sql, (new_val,))
                        self.load_data()
                        if self.on_change_cb:
                            self.on_change_cb()
                    except Exception as e:
                        messagebox.showerror("Hata", str(e))
            else:
                # VAR OLAN SATIRI GÜNCELLEME (UPDATE)
                sql = f"UPDATE {self.db.sanitize(self.table_name)} SET {self.db.sanitize(col_name)} = ? WHERE id = ?"
                try:
                    self.db.execute_query(sql, (new_val, row_id))
                    self.load_data()
                    if self.on_change_cb:
                        self.on_change_cb()
                except Exception as e:
                    messagebox.showerror("Hata", str(e))

        editor.bind("<Return>", save_inline_value)
        editor.bind("<FocusOut>", save_inline_value)

    def add_empty_row(self):
        cols_info = [ci for ci in self.db.get_table_columns(self.table_name) if ci['name'].lower() != 'id']
        if not cols_info:
            return

        first_col = cols_info[0]['name']
        try:
            sql = f"INSERT INTO {self.db.sanitize(self.table_name)} ({self.db.sanitize(first_col)}) VALUES (?)"
            self.db.execute_query(sql, ("Yeni Kayıt",))
            self.load_data()
            if self.on_change_cb:
                self.on_change_cb()
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    def delete_selected_row(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Uyarı", "Lütfen silmek istediğiniz satırı seçin!")
            return

        row_vals = self.tree.item(sel[0])["values"]
        row_id = row_vals[0]

        if str(row_id).startswith("*"):
            return

        if messagebox.askyesno("Onay", f"ID = {row_id} olan kayıt silinecektir. Devam edilsin mi?"):
            try:
                sql = f"DELETE FROM {self.db.sanitize(self.table_name)} WHERE id = ?"
                self.db.execute_query(sql, (row_id,))
                self.load_data()
                if self.on_change_cb:
                    self.on_change_cb()
            except Exception as e:
                messagebox.showerror("Hata", str(e))

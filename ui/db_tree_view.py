#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
from ui.data_editor import MSTDataEditor

class DBTreeView(ttk.LabelFrame):
    """MS Access Mimarisi 3. Faz: Veritabanı Ağacı ve Sürükle-Bırak İlişki Motoru"""

    def __init__(self, parent, db_engine, i18n_engine, ide_instance=None, **kwargs):
        super().__init__(parent, text="💾 MST Veritabanı & Şema Ağacı", padding=5, **kwargs)
        self.db = db_engine
        self.i18n = i18n_engine
        self.ide = ide_instance

        self.setup_ui()
        self.refresh_tree()

    def setup_ui(self):
        btn_bar = ttk.Frame(self)
        btn_bar.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        ttk.Button(btn_bar, text="➕ Yeni Tablo", command=self.add_table_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_bar, text="🔄 Yenile", command=self.refresh_tree).pack(side=tk.RIGHT, padx=2)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, selectmode="browse", show="tree")
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Sürükle - Bırak Olayları
        self.tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.tree.bind("<B1-Motion>", self.on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self.on_drag_release)

        self.drag_data = None

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        tables = self.db.get_tables()
        for tbl in tables:
            node = self.tree.insert("", tk.END, iid=f"tbl_{tbl}", text=f"📊 {tbl}", open=True)
            cols = self.db.get_table_columns(tbl)
            for c in cols:
                icon = "🔑 " if c["pk"] else "🔹 "
                self.tree.insert(node, tk.END, iid=f"col_{tbl}_{c['name']}", text=f"{icon}{c['name']} ({c['type']})")

    def add_table_dialog(self):
        win = tk.Toplevel(self)
        win.title("Yeni Tablo Oluştur")
        win.geometry("320x150")

        ttk.Label(win, text="Tablo Adı:").pack(pady=5)
        e_name = ttk.Entry(win, width=28)
        e_name.pack(pady=2)

        def create():
            t_name = e_name.get().strip().replace(" ", "_")
            if t_name:
                self.db.create_table(t_name, [{"name": "ad_soyad", "type": "TEXT"}])
                self.refresh_tree()
                win.destroy()

        ttk.Button(win, text="Tabloyu Oluştur", command=create).pack(pady=10)

    def on_double_click(self, event):
        item_id = self.tree.focus()
        if item_id.startswith("tbl_"):
            tbl_name = item_id.replace("tbl_", "")
            MSTDataEditor(self.winfo_toplevel(), self.db, tbl_name, on_change_cb=self.refresh_tree)

    def show_context_menu(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id.startswith("tbl_"):
            tbl_name = item_id.replace("tbl_", "")
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label=f"📊 '{tbl_name}' Verilerini Düzenle (Datasheet)", command=lambda: MSTDataEditor(self.winfo_toplevel(), self.db, tbl_name, on_change_cb=self.refresh_tree))
            menu.add_separator()
            menu.add_command(label="🗑️ Tabloyu Sil", command=lambda: self.delete_table(tbl_name))
            menu.tk_popup(event.x_root, event.y_root)

    def delete_table(self, tbl_name):
        if messagebox.askyesno("Tablo Silme Onayı", f"'{tbl_name}' tablosu ve içindeki tüm veriler silinecek! Emin misiniz?"):
            self.db.drop_table(tbl_name)
            self.refresh_tree()

    # Sürükle & Bırak ile Tuvala Veri Alanı Ekleme
    def on_drag_start(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id.startswith("col_"):
            parts = item_id.split("_")
            tbl = parts[1]
            fld = "_".join(parts[2:])
            self.drag_data = {"table": tbl, "field": fld}

    def on_drag_motion(self, event):
        if self.drag_data and self.ide:
            # Tuval üzerinde yeşil ekleme hayaletini güncelle
            canvas_widget = self.ide.canvas
            x = canvas_widget.canvas.winfo_pointerx() - canvas_widget.canvas.winfo_rootx()
            y = canvas_widget.canvas.winfo_pointery() - canvas_widget.canvas.winfo_rooty()
            canvas_widget.start_drag_field(self.drag_data)
            canvas_widget.update_drag_ghost(x, y)

    def on_drag_release(self, event):
        if self.drag_data and self.ide:
            canvas_widget = self.ide.canvas
            canvas_widget.on_canvas_release(event)
        self.drag_data = None

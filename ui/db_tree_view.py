#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from ui.data_editor import MSTDataEditor
from core.form_generator import MSTFormGenerator

class DBTreeView(ttk.LabelFrame):
    def __init__(self, parent, db_engine, i18n_engine, ide_instance=None, **kwargs):
        super().__init__(parent, text=i18n_engine.get("panel_db_tree", " 🗄️ MST Veritabanı & Şema Ağacı "), padding=5, **kwargs)
        self.db = db_engine
        self.i18n = i18n_engine
        self.ide_instance = ide_instance
        self.drag_data = None

        self.setup_ui()
        self.setup_context_menu()

    def setup_ui(self):
        self.tree = ttk.Treeview(self, show="tree headings", selectmode="browse")
        self.tree.heading("#0", text=self.i18n.get("lbl_schema_tree", "Tablo ve Sütun Yapısı"))
        self.tree.pack(fill=tk.BOTH, expand=True, pady=2)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, pady=2)

        ttk.Button(btn_frame, text=self.i18n.get("btn_refresh_schema", "🔄 Şemayı Yenile"), command=self.refresh_schema).pack(fill=tk.X)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click_node)
        self.tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.tree.bind("<B1-Motion>", self.on_drag_motion)
        
        self.refresh_schema()

    def on_drag_start(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            parent_item = self.tree.parent(item)
            if parent_item:  # Sütun düğümü
                tbl_name = parent_item.replace("tbl_", "")
                col_text = self.tree.item(item, "text")
                # İkonları temizleme
                col_name = col_text.replace("🔑 ", "").replace("🔹 ", "").split(" (")[0]
                
                self.drag_data = {
                    "table": tbl_name,
                    "field": col_name
                }
                if self.ide_instance and hasattr(self.ide_instance, 'canvas'):
                    self.ide_instance.canvas.start_drag_field(self.drag_data)

    def on_drag_motion(self, event):
        if self.drag_data and self.ide_instance and hasattr(self.ide_instance, 'canvas'):
            # Tuval üzerindeki fare konumuna göre ön izleme
            canvas_widget = self.ide_instance.canvas.canvas
            x = canvas_widget.winfo_pointerx() - canvas_widget.winfo_rootx()
            y = canvas_widget.winfo_pointery() - canvas_widget.winfo_rooty()
            self.ide_instance.canvas.update_drag_ghost(x, y)

    def setup_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="📊 Veri Sayfası (Datasheet - Doğrudan Düzenle)", command=self.open_data_editor)
        self.context_menu.add_command(label="✨ Bu Tablodan Otomatik Form Oluştur", command=self.generate_auto_form)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="➕ Yeni Tablo Ekle", command=self.add_table_dialog)
        self.context_menu.add_command(label="➕ Sütun Ekle", command=self.add_column_dialog)
        self.context_menu.add_command(label="🔗 Yabancı Anahtar İlişkisi Kur", command=self.add_foreign_key_dialog)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Tabloyu Sil", command=self.delete_table)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def on_double_click_node(self, event):
        sel = self.tree.selection()
        if sel:
            node_id = sel[0]
            if node_id.startswith("tbl_"):
                self.open_data_editor()

    def generate_auto_form(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Uyarı", "Lütfen otomatik form oluşturmak istediğiniz tabloyu seçin!")
            return

        node_id = sel[0]
        tbl_name = node_id.replace("tbl_", "") if node_id.startswith("tbl_") else None
        if not tbl_name:
            messagebox.showwarning("Uyarı", "Lütfen bir tablo düğümü seçin.")
            return

        cols_info = self.db.get_table_columns(tbl_name)
        comps = MSTFormGenerator.generate_form_for_table(tbl_name, cols_info)

        page_name = f"Form_{tbl_name.title()}"

        if self.ide_instance and hasattr(self.ide_instance, 'add_custom_page'):
            self.ide_instance.add_custom_page(page_name, comps)
            messagebox.showinfo("MST Studio", f"🎉 '{page_name}' formu başarıyla oluşturuldu ve tuvale yüklendi!")

    def open_data_editor(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Uyarı", "Lütfen bir tablo seçin!")
            return

        node_id = sel[0]
        tbl_name = node_id.replace("tbl_", "") if node_id.startswith("tbl_") else None
        if not tbl_name:
            messagebox.showwarning("Uyarı", "Lütfen bir tablo seçin (sütun seçilemez).")
            return

        MSTDataEditor(self.winfo_toplevel(), self.db, tbl_name, on_change_cb=self.refresh_schema)

    def refresh_schema(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        tables = self.db.get_tables()
        for tbl in tables:
            tbl_node = self.tree.insert("", tk.END, iid=f"tbl_{tbl}", text=f"📊 {tbl}", open=True)
            cols = self.db.get_table_columns(tbl)
            for col in cols:
                pk_icon = "🔑 " if col["pk"] else "🔹 "
                self.tree.insert(tbl_node, tk.END, text=f"{pk_icon}{col['name']} ({col['type']})")

    def add_table_dialog(self):
        tbl_name = simpledialog.askstring("Yeni Tablo", "Oluşturulacak Tablo Adı:", parent=self)
        if tbl_name:
            clean_name = self.db.sanitize(tbl_name)
            if clean_name:
                self.db.create_table(clean_name, [{"name": "ad", "type": "TEXT"}])
                self.refresh_schema()

    def add_column_dialog(self):
        sel = self.tree.selection()
        if not sel:
            return

        node_id = sel[0]
        tbl_name = node_id.replace("tbl_", "") if node_id.startswith("tbl_") else None
        if not tbl_name:
            return

        col_win = tk.Toplevel(self)
        col_win.title(f"Sütun Ekle - [{tbl_name}]")
        col_win.geometry("320x180")

        ttk.Label(col_win, text="Sütun Adı:").pack(pady=5)
        e_col_name = ttk.Entry(col_win, width=25)
        e_col_name.pack(pady=2)

        ttk.Label(col_win, text="Veri Tipi:").pack(pady=5)
        cb_col_type = ttk.Combobox(col_win, values=["TEXT", "INTEGER", "REAL", "DATE", "BOOLEAN"], width=22, state="readonly")
        cb_col_type.current(0)
        cb_col_type.pack(pady=2)

        def save_column():
            c_name = self.db.sanitize(e_col_name.get())
            c_type = cb_col_type.get()
            if c_name:
                sql = f"ALTER TABLE {self.db.sanitize(tbl_name)} ADD COLUMN {c_name} {c_type};"
                try:
                    self.db.execute_query(sql)
                    self.refresh_schema()
                    col_win.destroy()
                except Exception as e:
                    messagebox.showerror("Hata", str(e))

        ttk.Button(col_win, text="Ekle", command=save_column).pack(pady=10)

    def add_foreign_key_dialog(self):
        tables = self.db.get_tables()
        if len(tables) < 2:
            return

        fk_win = tk.Toplevel(self)
        fk_win.title("Görsel Yabancı Anahtar (FK) İlişkisi Kur")
        fk_win.geometry("360x240")

        ttk.Label(fk_win, text="Kaynak Tablo (FK Eklenecek):").pack(pady=3)
        cb_source_tbl = ttk.Combobox(fk_win, values=tables, width=28, state="readonly")
        cb_source_tbl.pack(pady=2)

        ttk.Label(fk_win, text="Hedef / Referans Tablo (PK):").pack(pady=3)
        cb_ref_tbl = ttk.Combobox(fk_win, values=tables, width=28, state="readonly")
        cb_ref_tbl.pack(pady=2)

        ttk.Label(fk_win, text="FK Sütun Adı (Örn: kategori_id):").pack(pady=3)
        e_fk_col = ttk.Entry(fk_win, width=30)
        e_fk_col.pack(pady=2)

        def create_fk_relation():
            src = cb_source_tbl.get()
            ref = cb_ref_tbl.get()
            fk_col = self.db.sanitize(e_fk_col.get())

            if src and ref and fk_col:
                try:
                    sql = f"ALTER TABLE {self.db.sanitize(src)} ADD COLUMN {fk_col} INTEGER REFERENCES {self.db.sanitize(ref)}(id);"
                    self.db.execute_query(sql)
                    self.refresh_schema()
                    fk_win.destroy()
                except Exception as e:
                    messagebox.showerror("Hata", str(e))

        ttk.Button(fk_win, text="İlişkiyi Kaydet", command=create_fk_relation).pack(pady=12)

    def delete_table(self):
        sel = self.tree.selection()
        if not sel: return
        node_id = sel[0]
        tbl_name = node_id.replace("tbl_", "") if node_id.startswith("tbl_") else None
        if tbl_name and messagebox.askyesno("Onay", f"'{tbl_name}' silinsin mi?"):
            self.db.drop_table(tbl_name)
            self.refresh_schema()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

class LiveSimulator(tk.Toplevel):
    """MS Access Mimarisi 2. Faz: Gezinti Çubuğu (Navigation Bar), Tam Otomatik Veri Bağlama & Makro Motoru"""

    def __init__(self, parent, db_engine, i18n_engine, pages, page_components, active_page="Giris_Sayfasi"):
        super().__init__(parent)
        self.db = db_engine
        self.i18n = i18n_engine
        self.pages = pages
        self.page_components = page_components
        self.active_page = active_page

        self.title(f"▶ MST Studio Live Runtime - [{active_page}]")
        self.geometry("1140x780")

        self.form_inputs = {}  # {field_name: (widget_type, widget_instance)}
        self.active_records = []
        self.current_record_index = -1
        self.active_table_name = ""
        self.main_grid_tree = None

        self.setup_ui()
        self.render_page(self.active_page)

    def setup_ui(self):
        # Sol Menü
        self.sidebar = ttk.Frame(self, width=200, padding=10, relief="groove")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Ana Çalışma Alanı
        self.main_container = ttk.Frame(self)
        self.main_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.viewport = tk.Canvas(self.main_container, bg="#ffffff", highlightthickness=0)
        self.viewport.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # MS Access Tarzı Gezinti Çubuğu (Navigation Bar)
        self.nav_bar = ttk.Frame(self.main_container, padding=4, relief="raised")
        self.nav_bar.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Button(self.nav_bar, text="|◄", width=4, command=self.nav_first).pack(side=tk.LEFT, padx=1)
        ttk.Button(self.nav_bar, text="◄", width=4, command=self.nav_prev).pack(side=tk.LEFT, padx=1)
        
        ttk.Label(self.nav_bar, text=" Kayıt: ").pack(side=tk.LEFT, padx=(5, 0))
        self.lbl_record_count = ttk.Label(self.nav_bar, text="0 / 0", font=("Helvetica", 9, "bold"))
        self.lbl_record_count.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(self.nav_bar, text="►", width=4, command=self.nav_next).pack(side=tk.LEFT, padx=1)
        ttk.Button(self.nav_bar, text="►|", width=4, command=self.nav_last).pack(side=tk.LEFT, padx=1)
        ttk.Button(self.nav_bar, text="➕ Yeni Kayıt", command=self.nav_new).pack(side=tk.LEFT, padx=10)

    def update_sidebar(self):
        for w in self.sidebar.winfo_children():
            w.destroy()

        ttk.Label(self.sidebar, text="📌 Form Menüsü", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=5)
        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        for p_name in self.pages.keys():
            btn = ttk.Button(self.sidebar, text=f"📋 {p_name}", command=lambda p=p_name: self.render_page(p))
            btn.pack(fill=tk.X, pady=2)

    def render_page(self, page_name):
        self.active_page = page_name
        self.form_inputs = {}
        self.active_records = []
        self.current_record_index = -1
        self.active_table_name = ""

        self.viewport.delete("all")
        for child in self.viewport.winfo_children():
            child.destroy()

        self.update_sidebar()
        comps = self.page_components.get(page_name, [])

        self.main_grid_tree = None
        subform_comps = []

        for c in comps:
            x, y, w, h = c['x'], c['y'], c['w'], c['h']
            tbl = c.get('table', '')
            fld = c.get('field', '')

            if tbl and not self.active_table_name and c['type'] != "Alt Form (Master-Detail)":
                self.active_table_name = tbl

            if c['type'] == "Etiket":
                lbl = tk.Label(self.viewport, text=c['text'], font=("Helvetica", 9), bg="#ffffff", anchor="w")
                lbl.place(x=x, y=y, width=w, height=h)

            elif c['type'] == "Metin Kutusu":
                ent = ttk.Entry(self.viewport)
                ent.place(x=x, y=y, width=w, height=h)
                if fld:
                    self.form_inputs[fld] = ("entry", ent)

            elif c['type'] == "Açılır Liste":
                cb = ttk.Combobox(self.viewport, state="readonly")
                if tbl and fld:
                    try:
                        rows = self.db.get_table_data(tbl)
                        vals = [str(r.get(fld, '')) for r in rows if r.get(fld)]
                        cb['values'] = list(dict.fromkeys(vals))
                    except Exception:
                        pass
                cb.place(x=x, y=y, width=w, height=h)
                if fld:
                    self.form_inputs[fld] = ("combo", cb)

            elif c['type'] == "Onay Kutusu":
                var = tk.BooleanVar()
                chk = ttk.Checkbutton(self.viewport, text=c['text'], variable=var)
                chk.place(x=x, y=y, width=w, height=h)
                if fld:
                    self.form_inputs[fld] = ("check", var)

            elif c['type'] == "Veri Tablosu":
                grid_container = ttk.Frame(self.viewport)
                grid_container.place(x=x, y=y, width=w, height=h)
                
                tbl_name = c.get('table', '')
                tree = ttk.Treeview(grid_container, show="headings", selectmode="browse")
                vsb = ttk.Scrollbar(grid_container, orient="vertical", command=tree.yview)
                tree.configure(yscrollcommand=vsb.set)
                
                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                vsb.pack(side=tk.RIGHT, fill=tk.Y)

                if tbl_name:
                    try:
                        cols_info = self.db.get_table_columns(tbl_name)
                        cols = [col["name"] for col in cols_info]
                        tree["columns"] = cols
                        for col in cols:
                            tree.heading(col, text=col.upper())
                            tree.column(col, width=90)

                        rows = self.db.get_table_data(tbl_name)
                        for row in rows:
                            tree.insert("", tk.END, iid=str(row.get('id', '')), values=[row[col] for col in cols])
                    except Exception:
                        pass

                self.main_grid_tree = tree

            elif c['type'] == "Alt Form (Master-Detail)":
                subform_comps.append((c, x, y, w, h))

            elif c['type'] == "Buton":
                act = c.get('action', 'Kaydet / Güncelle (Save/Update)')
                target = c.get('target', '')
                btn = ttk.Button(self.viewport, text=c['text'], command=lambda a=act, t=target: self.handle_button_click(a, t))
                btn.place(x=x, y=y, width=w, height=h)

        # Tablo Kayıt Tıklama Dinleyicisi
        if self.main_grid_tree and self.active_table_name:
            def on_tree_select(event):
                sel = self.main_grid_tree.selection()
                if sel:
                    rec_id = sel[0]
                    for idx, r in enumerate(self.active_records):
                        if str(r.get('id', '')) == str(rec_id):
                            self.current_record_index = idx
                            self.bind_current_record_to_form()
                            break

            self.main_grid_tree.bind("<<TreeviewSelect>>", on_tree_select)

        # Alt Form Bağlantıları
        for c, x, y, w, h in subform_comps:
            container = ttk.LabelFrame(self.viewport, text=f" 🔗 Alt Form: [{c.get('table', '')}] ", padding=5)
            container.place(x=x, y=y, width=w, height=h)

            sub_tree = ttk.Treeview(container, show="headings")
            sub_tree.pack(fill=tk.BOTH, expand=True)

            tbl_name = c.get('table', '')
            detail_fk = c.get('detail_field', '')

            if tbl_name:
                cols_info = self.db.get_table_columns(tbl_name)
                cols = [col["name"] for col in cols_info]
                sub_tree["columns"] = cols
                for col in cols:
                    sub_tree.heading(col, text=col.upper())
                    sub_tree.column(col, width=90)

            if self.main_grid_tree and tbl_name and detail_fk:
                def on_subform_filter(event, st=sub_tree, t_name=tbl_name, fk=detail_fk):
                    sel = self.main_grid_tree.selection()
                    if sel:
                        master_id = sel[0]
                        for item in st.get_children():
                            st.delete(item)

                        sql = f"SELECT * FROM {self.db.sanitize(t_name)} WHERE {self.db.sanitize(fk)} = ?"
                        try:
                            cursor = self.db.execute_query(sql, (master_id,))
                            rows = cursor.fetchall()
                            for row in rows:
                                st.insert("", tk.END, values=list(row))
                        except Exception:
                            pass

                self.main_grid_tree.bind("<<TreeviewSelect>>", on_subform_filter, add="+")

        # Form Verilerini Yükle
        self.reload_active_records()

    def reload_active_records(self):
        """Veritabanındaki aktif tablo verilerini yükler ve gezinti çubuğunu günceller."""
        if self.active_table_name:
            try:
                self.active_records = self.db.get_table_data(self.active_table_name)
                if self.active_records:
                    if self.current_record_index < 0 or self.current_record_index >= len(self.active_records):
                        self.current_record_index = 0
                    self.bind_current_record_to_form()
                else:
                    self.current_record_index = -1
                    self.nav_new()
            except Exception:
                self.active_records = []
                self.current_record_index = -1
        self.update_nav_bar_label()

    def bind_current_record_to_form(self):
        """Mevcut kaydı form alanlarına doldurur."""
        if 0 <= self.current_record_index < len(self.active_records):
            rec = self.active_records[self.current_record_index]
            for fld_name, (w_type, widget) in self.form_inputs.items():
                val = str(rec.get(fld_name, ''))
                if w_type == "entry":
                    widget.delete(0, tk.END)
                    widget.insert(0, val)
                elif w_type == "combo":
                    widget.set(val)
                elif w_type == "check":
                    widget.set(bool(val and val != '0'))

            if self.main_grid_tree and 'id' in rec:
                rec_id_str = str(rec['id'])
                if self.main_grid_tree.exists(rec_id_str):
                    self.main_grid_tree.selection_set(rec_id_str)

        self.update_nav_bar_label()

    def update_nav_bar_label(self):
        total = len(self.active_records)
        curr = self.current_record_index + 1 if total > 0 and self.current_record_index >= 0 else 0
        self.lbl_record_count.config(text=f"{curr} / {total}")

    # Gezinti Çubuğu Komutları
    def nav_first(self):
        if self.active_records:
            self.current_record_index = 0
            self.bind_current_record_to_form()

    def nav_prev(self):
        if self.active_records and self.current_record_index > 0:
            self.current_record_index -= 1
            self.bind_current_record_to_form()

    def nav_next(self):
        if self.active_records and self.current_record_index < len(self.active_records) - 1:
            self.current_record_index += 1
            self.bind_current_record_to_form()

    def nav_last(self):
        if self.active_records:
            self.current_record_index = len(self.active_records) - 1
            self.bind_current_record_to_form()

    def nav_new(self):
        self.current_record_index = -1
        for fld_name, (w_type, widget) in self.form_inputs.items():
            if w_type == "entry":
                widget.delete(0, tk.END)
            elif w_type == "combo":
                widget.set("")
            elif w_type == "check":
                widget.set(False)
        self.update_nav_bar_label()

    def handle_button_click(self, action, target_page):
        """Makro / Eylem Yürütücüsü"""
        if "Kaydet" in action:
            if not self.active_table_name:
                messagebox.showwarning("Uyarı", "Bağlı veritabanı tablosu yok!")
                return

            data = {}
            for fld_name, (w_type, widget) in self.form_inputs.items():
                if w_type in ["entry", "combo"]:
                    data[fld_name] = widget.get().strip()
                elif w_type == "check":
                    data[fld_name] = 1 if widget.get() else 0

            if not data:
                return

            if 0 <= self.current_record_index < len(self.active_records):  # UPDATE
                rec_id = self.active_records[self.current_record_index].get('id')
                set_clause = ", ".join([f"{self.db.sanitize(k)} = ?" for k in data.keys()])
                sql = f"UPDATE {self.db.sanitize(self.active_table_name)} SET {set_clause} WHERE id = ?"
                self.db.execute_query(sql, list(data.values()) + [rec_id])
                messagebox.showinfo("Başarılı", "Kayıt güncellendi!")
            else:  # INSERT
                cols = ", ".join([self.db.sanitize(k) for k in data.keys()])
                placeholders = ", ".join(["?" for _ in data.keys()])
                sql = f"INSERT INTO {self.db.sanitize(self.active_table_name)} ({cols}) VALUES ({placeholders})"
                self.db.execute_query(sql, tuple(data.values()))
                messagebox.showinfo("Başarılı", "Yeni kayıt eklendi!")

            self.reload_active_records()

        elif "Yeni Kayıt" in action:
            self.nav_new()

        elif "Sil" in action:
            if 0 <= self.current_record_index < len(self.active_records):
                rec_id = self.active_records[self.current_record_index].get('id')
                if messagebox.askyesno("Onay", "Kayıt kalıcı olarak silinsin mi?"):
                    sql = f"DELETE FROM {self.db.sanitize(self.active_table_name)} WHERE id = ?"
                    self.db.execute_query(sql, (rec_id,))
                    messagebox.showinfo("Başarılı", "Kayıt silindi!")
                    self.reload_active_records()

        elif "Sonraki" in action:
            self.nav_next()

        elif "Önceki" in action:
            self.nav_prev()

        elif "Sayfa" in action or "Giriş" in action:
            if target_page and target_page in self.pages:
                self.render_page(target_page)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from core.action_engine import MSTActionEngine

class LiveSimulator(tk.Toplevel):
    def __init__(self, parent, db_engine, i18n_engine, pages_dict, page_components_dict, active_page="Giris_Sayfasi"):
        super().__init__(parent)
        self.db = db_engine
        self.i18n = i18n_engine
        self.pages = pages_dict
        self.components = page_components_dict
        self.active_page = active_page

        self.title("MST Studio - Live Application Preview")
        self.geometry("1020x700")

        self.session = {"user": None, "role": None}
        self.action_engine = MSTActionEngine(self.db, self)
        self.selected_row_id = None

        self.setup_ui()
        self.render_page(self.active_page)

    def setup_ui(self):
        self.sidebar = ttk.Frame(self, width=180, padding=10, relief="groove")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.viewport = tk.Canvas(self, bg="#f9f9f9", highlightthickness=0)
        self.viewport.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def update_sidebar(self):
        for w in self.sidebar.winfo_children():
            w.destroy()

        ttk.Label(self.sidebar, text="📌 Sayfa Menüsü", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=5)
        
        user_disp = self.session["user"] or "Açılmadı"
        role_disp = self.session["role"] or "Herkes"
        
        ttk.Label(self.sidebar, text=f"Oturum: {user_disp}\nYetki: {role_disp}", font=("Helvetica", 8, "italic")).pack(anchor=tk.W, pady=5)
        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)

        for p_name, p_info in self.pages.items():
            req_role = p_info.get("role", "Herkes")
            if req_role == "Herkes" or role_disp == "Admin" or role_disp == req_role:
                ttk.Button(self.sidebar, text=p_name, command=lambda p=p_name: self.render_page(p)).pack(fill=tk.X, pady=2)

    def validate_inputs(self, page_comps, inputs_map):
        for c in page_comps:
            if c['type'] in ["Metin Kutusu", "Açılır Liste"]:
                fld = c.get('field')
                if not fld or fld not in inputs_map:
                    continue

                entry_widget = inputs_map[fld][0]
                val = entry_widget.get().strip() if hasattr(entry_widget, 'get') else ""

                if c.get("is_required", False) and not val:
                    msg = c.get("validation_msg") or f"'{c.get('text', fld)}' alanı boş bırakılamaz!"
                    messagebox.showwarning("Doğrulama Uyarısı", msg)
                    if hasattr(entry_widget, 'focus_set'):
                        entry_widget.focus_set()
                    return False

        return True

    def populate_form_from_row(self, tree, inputs_map, tbl_name):
        sel = tree.selection()
        if not sel:
            return

        row_vals = tree.item(sel[0])["values"]
        cols = tree["columns"]

        if not row_vals or not cols:
            return

        self.selected_row_id = row_vals[0]
        col_val_map = dict(zip(cols, row_vals))

        for fld, (widget, t_name) in inputs_map.items():
            if fld in col_val_map:
                val = str(col_val_map[fld])
                if isinstance(widget, ttk.Entry):
                    widget.delete(0, tk.END)
                    widget.insert(0, val)
                elif isinstance(widget, ttk.Combobox):
                    widget.set(val)

    def clear_form_inputs(self, inputs_map):
        self.selected_row_id = None
        for fld, (widget, t_name) in inputs_map.items():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, ttk.Combobox):
                if widget['values']:
                    widget.current(0)

    def add_quick_lookup_record(self, lookup_tbl, cb_widget):
        """Açılır kutudan çıkmadan ilişkili tabloya hızlı yeni veri ekler."""
        cols = [ci['name'] for ci in self.db.get_table_columns(lookup_tbl) if ci['name'].lower() != 'id']
        if not cols:
            return

        target_col = cols[0]
        new_val = simpledialog.askstring("Hızlı Ekle", f"Yeni '{lookup_tbl.upper()}' kaydını girin:", parent=self)
        if new_val:
            try:
                sql = f"INSERT INTO {self.db.sanitize(lookup_tbl)} ({self.db.sanitize(target_col)}) VALUES (?)"
                self.db.execute_query(sql, (new_val.strip(),))
                
                # Açılır kutu verilerini canlı yenile
                cur = self.db.execute_query(f"SELECT {self.db.sanitize(target_col)} FROM {self.db.sanitize(lookup_tbl)}")
                updated_options = [str(r[0]) for r in cur.fetchall()]
                cb_widget['values'] = updated_options
                cb_widget.set(new_val.strip())
                messagebox.showinfo("Başarılı", f"'{new_val}' kaydı {lookup_tbl} tablosuna eklendi!")
            except Exception as e:
                messagebox.showerror("Hata", str(e))

    def render_page(self, page_name):
        self.active_page = page_name
        self.selected_row_id = None
        self.viewport.delete("all")
        for child in self.viewport.winfo_children():
            child.destroy()

        self.update_sidebar()

        page_info = self.pages.get(page_name, {})
        req = page_info.get("role", "Herkes")

        if req != "Herkes" and self.session["role"] != req and self.session["role"] != "Admin":
            lbl = tk.Label(self.viewport, text="⚠️ Yetkisiz Erişim!\nBu sayfayı görüntüleme izniniz yok.", font=("Helvetica", 14, "bold"), fg="red", bg="#f9f9f9")
            lbl.place(x=150, y=150)
            return

        comps = self.components.get(page_name, [])
        inputs = {}
        tree_widgets = {}

        for c in comps:
            x, y, w, h = c['x'], c['y'], c['w'], c['h']

            if c['type'] == "Etiket":
                lbl = tk.Label(self.viewport, text=c['text'], font=("Helvetica", 9), bg="#f9f9f9", anchor="w")
                lbl.place(x=x, y=y, width=w, height=h)

            elif c['type'] == "Metin Kutusu":
                ent = ttk.Entry(self.viewport)
                ent.place(x=x, y=y, width=w, height=h)
                inputs[c['field']] = (ent, c['table'])

            elif c['type'] == "Açılır Liste":
                fld = c.get('field', '')
                lookup_tbl = c.get('lookup_table') or (fld if fld in self.db.get_tables() else None)
                if not lookup_tbl and fld:
                    for t in self.db.get_tables():
                        if t in fld.lower() or fld.lower() in t:
                            lookup_tbl = t
                            break

                cb_frame = ttk.Frame(self.viewport)
                cb_frame.place(x=x, y=y, width=w, height=h)

                cb = ttk.Combobox(cb_frame, state="readonly")
                cb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                options = [opt.strip() for opt in c.get('options', '').split(',') if opt.strip()]

                if lookup_tbl:
                    try:
                        cols = [ci['name'] for ci in self.db.get_table_columns(lookup_tbl) if ci['name'].lower() != 'id']
                        if cols:
                            disp_col = cols[0]
                            cursor = self.db.execute_query(f"SELECT {self.db.sanitize(disp_col)} FROM {self.db.sanitize(lookup_tbl)}")
                            options = [str(r[0]) for r in cursor.fetchall()]
                    except Exception:
                        pass

                    btn_add_quick = ttk.Button(cb_frame, text="➕", width=3, command=lambda lt=lookup_tbl, cbw=cb: self.add_quick_lookup_record(lt, cbw))
                    btn_add_quick.pack(side=tk.RIGHT, padx=1)

                cb['values'] = options
                if options:
                    cb.current(0)

                inputs[c['field']] = (cb, c['table'])

            elif c['type'] == "Veri Tablosu":
                grid_container = ttk.Frame(self.viewport)
                grid_container.place(x=x, y=y, width=w, height=h)

                tbl_name = c.get('table', '')
                btn_bar = ttk.Frame(grid_container)
                btn_bar.pack(side=tk.TOP, fill=tk.X, pady=2)

                def export_csv_act(t=tbl_name):
                    self.action_engine.execute_chain([{"type": "export_report", "table": t, "format": "csv"}], inputs, comps, page_name)

                def export_html_act(t=tbl_name):
                    self.action_engine.execute_chain([{"type": "export_report", "table": t, "format": "html"}], inputs, comps, page_name)

                ttk.Button(btn_bar, text="📊 CSV", command=export_csv_act).pack(side=tk.RIGHT, padx=2)
                ttk.Button(btn_bar, text="📄 HTML", command=export_html_act).pack(side=tk.RIGHT, padx=2)
                ttk.Button(btn_bar, text="➕ Temizle / Yeni Kayıt", command=lambda: self.clear_form_inputs(inputs)).pack(side=tk.LEFT, padx=2)

                tree = ttk.Treeview(grid_container, show="headings", selectmode="browse")
                tree.pack(fill=tk.BOTH, expand=True)
                tree_widgets[tbl_name] = tree

                grid_menu = tk.Menu(self, tearoff=0)
                grid_menu.add_command(label="✏️ Seçili Kaydı Düzenle", command=lambda t=tree, tn=tbl_name: self.populate_form_from_row(t, inputs, tn))
                grid_menu.add_command(label="🗑️ Seçili Kaydı Sil", command=lambda t=tree, tn=tbl_name: self.delete_row_act(t, tn))

                def show_grid_menu(event, menu=grid_menu, t=tree):
                    item = t.identify_row(event.y)
                    if item:
                        t.selection_set(item)
                        menu.tk_popup(event.x_root, event.y_root)

                tree.bind("<Button-3>", show_grid_menu)
                tree.bind("<Double-1>", lambda ev, t=tree, tn=tbl_name: self.populate_form_from_row(t, inputs, tn))

                if tbl_name:
                    self.refresh_grid_data(tree, tbl_name)

            elif c['type'] == "Buton":
                def click(item=c):
                    act = item.get('action', '')
                    chain = [{"type": "validate_inputs"}]

                    if act == "Kullanıcı Girişi Yap":
                        chain.append({"type": "login_user"})
                        chain.append({"type": "show_message", "text": f"Giriş Başarılı!\nHoş geldiniz."})
                        chain.append({"type": "navigate", "target": item.get('target', 'Ana_Sayfa')})
                    elif act == "Kayıt Ekle":
                        chain.append({"type": "save_or_update_record"})
                        if item.get('target'):
                            chain.append({"type": "navigate", "target": item.get('target')})
                    elif act == "Sayfaya Git":
                        chain.append({"type": "navigate", "target": item.get('target')})

                    self.action_engine.execute_chain(chain, inputs, comps, page_name)

                btn = ttk.Button(self.viewport, text=c['text'], command=click)
                btn.place(x=x, y=y, width=w, height=h)

    def refresh_grid_data(self, tree, tbl_name):
        for item in tree.get_children():
            tree.delete(item)

        try:
            cols_info = self.db.get_table_columns(tbl_name)
            cols = [ci['name'] for ci in cols_info]
            tree["columns"] = cols
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=90)

            cursor = self.db.execute_query(f"SELECT * FROM {self.db.sanitize(tbl_name)}")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)
        except Exception:
            pass

    def delete_row_act(self, tree, tbl_name):
        sel = tree.selection()
        if not sel:
            return

        row_vals = tree.item(sel[0])["values"]
        row_id = row_vals[0]

        if messagebox.askyesno("Silme Onayı", f"ID = {row_id} olan kayıt silinecektir. Devam edilsin mi?"):
            try:
                self.db.execute_query(f"DELETE FROM {self.db.sanitize(tbl_name)} WHERE id = ?", (row_id,))
                self.refresh_grid_data(tree, tbl_name)
                messagebox.showinfo("Başarılı", "Kayıt silindi.")
            except Exception as e:
                messagebox.showerror("Hata", str(e))

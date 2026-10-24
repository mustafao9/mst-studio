#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

from core.i18n_engine import i18n
from core.db_engine import DatabaseEngine
from core.filter_engine import FilterEngine
from core.project_engine import MSTProjectEngine
from core.theme_engine import MSTThemeEngine

from ui.db_tree_view import DBTreeView
from ui.designer_canvas import DesignerCanvas
from ui.property_sheet import MSTPropertySheet
from ui.packager_dialog import MSTPackagerDialog
from preview.live_simulator import LiveSimulator

class MSTStudioIDE:
    def __init__(self, root):
        self.root = root
        self.root.app = self
        
        self.theme_engine = MSTThemeEngine()
        self.project_engine = MSTProjectEngine("Varsayilan_Proje")
        self.project_dir = os.path.join(os.getcwd(), "projects", "Varsayilan_Proje")
        if not os.path.exists(self.project_dir):
            os.makedirs(self.project_dir)

        self.db_path = os.path.join(self.project_dir, "mst_database.db")
        self.db_engine = DatabaseEngine(self.db_path)
        self.filter_engine = FilterEngine(self.db_engine)

        self.root.title("MST Studio - Professional Visual Application Builder")
        self.root.geometry("1480x920")

        self.pages = {
            "Giris_Sayfasi": {"is_login": True, "role": "Herkes"},
            "Ana_Sayfa": {"is_login": False, "role": "Herkes"}
        }
        self.active_page = "Giris_Sayfasi"

        self.page_components = {
            "Giris_Sayfasi": [
                {"id": 1, "type": "Etiket", "x": 40, "y": 40, "w": 100, "h": 25, "text": "Kullanıcı Adı:", "table": "", "field": ""},
                {"id": 2, "type": "Metin Kutusu", "x": 150, "y": 38, "w": 180, "h": 28, "text": "", "table": "kullanicilar", "field": "kullanici_adi", "is_required": True, "validation_rule": "Yok", "validation_msg": "Kullanıcı adı boş bırakılamaz!"},
                {"id": 3, "type": "Etiket", "x": 40, "y": 85, "w": 100, "h": 25, "text": "Şifre:", "table": "", "field": ""},
                {"id": 4, "type": "Metin Kutusu", "x": 150, "y": 83, "w": 180, "h": 28, "text": "", "table": "kullanicilar", "field": "sifre", "is_required": True, "validation_rule": "Yok", "validation_msg": "Şifre boş bırakılamaz!"},
                {"id": 5, "type": "Buton", "x": 150, "y": 130, "w": 180, "h": 35, "text": "🔑 Giriş Yap", "action": "Kullanıcı Girişi Yap", "target": "Ana_Sayfa"}
            ],
            "Ana_Sayfa": [
                {"id": 1, "type": "Etiket", "x": 40, "y": 30, "w": 320, "h": 30, "text": "Hoş Geldiniz! MST Studio Yönetim Paneli"},
                {"id": 2, "type": "Veri Tablosu", "x": 40, "y": 80, "w": 520, "h": 260, "table": "kullanicilar", "field": ""}
            ]
        }

        self.setup_ui()
        self.theme_engine.apply_theme_to_root(self.root)
        self.load_page(self.active_page)

        # Çift tıklama ile dışarıdan .mst dosyası gönderilmişse otomatik aç
        if len(sys.argv) > 1:
            passed_file = sys.argv[1]
            if os.path.exists(passed_file) and passed_file.endswith(".mst"):
                self.load_mst_file_from_path(passed_file)

    def setup_ui(self):
        toolbar = ttk.Frame(self.root, padding=5)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(toolbar, text="💾 Projeyi Kaydet (.mst)", command=self.save_project_file).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="📂 Projeyi Aç (.mst)", command=self.open_project_file).pack(side=tk.LEFT, padx=3)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        ttk.Button(toolbar, text="📄 Yeni Form", command=self.add_page_dialog).pack(side=tk.LEFT, padx=3)
        ttk.Button(toolbar, text="📦 Bağımsız Uygulama Paketle (Exe/Bundle)", command=self.open_packager_dialog).pack(side=tk.LEFT, padx=6)

        btn_run = tk.Button(toolbar, text="▶ Uygulamayı Çalıştır (F5)", bg="#2eb85c", fg="white", font=("Helvetica", 10, "bold"), command=self.run_preview)
        btn_run.pack(side=tk.LEFT, padx=15)

        ttk.Button(toolbar, text="🌙 / ☀️ Tema Değiştir", command=self.toggle_theme).pack(side=tk.RIGHT, padx=5)

        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_paned = ttk.PanedWindow(main_paned, orient=tk.VERTICAL)
        main_paned.add(left_paned, weight=2)

        pages_frame = ttk.LabelFrame(left_paned, text=" Formlar & Sayfa Yetkileri ", padding=5)
        left_paned.add(pages_frame, weight=1)

        self.pages_listbox = tk.Listbox(pages_frame, font=("Helvetica", 10))
        self.pages_listbox.pack(fill=tk.BOTH, expand=True, pady=2)
        self.pages_listbox.bind("<<ListboxSelect>>", self.on_page_select)
        self.pages_listbox.bind("<Button-3>", self.show_page_context_menu)
        self.refresh_pages_list()

        self.page_context_menu = tk.Menu(self.root, tearoff=0)
        self.page_context_menu.add_command(label="✏️ Form İsmini Değiştir (Rename)", command=self.rename_selected_page)
        self.page_context_menu.add_command(label="📋 Form Kopyasını Oluştur (Duplicate)", command=self.duplicate_selected_page)
        self.page_context_menu.add_separator()
        self.page_context_menu.add_command(label="🗑️ Formu Sil", command=self.delete_selected_page)

        self.db_tree_view = DBTreeView(left_paned, self.db_engine, i18n, ide_instance=self)
        left_paned.add(self.db_tree_view, weight=2)

        center_frame = ttk.Frame(main_paned, padding=5)
        main_paned.add(center_frame, weight=7)

        palette = ttk.LabelFrame(center_frame, text=" MST Form Denetim Araçları ", padding=5)
        palette.pack(side=tk.TOP, fill=tk.X, pady=2)

        ttk.Button(palette, text="↖ Seç & Taş", command=lambda: self.canvas.set_tool("select")).pack(side=tk.LEFT, padx=2)
        ttk.Button(palette, text="🔤 Etiket", command=lambda: self.canvas.set_tool("label")).pack(side=tk.LEFT, padx=2)
        ttk.Button(palette, text="✏️ Metin Kutusu", command=lambda: self.canvas.set_tool("input")).pack(side=tk.LEFT, padx=2)
        ttk.Button(palette, text="🔽 Açılır Liste", command=lambda: self.canvas.set_tool("select")).pack(side=tk.LEFT, padx=2)
        ttk.Button(palette, text="☑️ Onay Kutusu", command=lambda: self.canvas.set_tool("checkbox")).pack(side=tk.LEFT, padx=2)
        ttk.Button(palette, text="🔘 Buton", command=lambda: self.canvas.set_tool("button")).pack(side=tk.LEFT, padx=2)
        ttk.Button(palette, text="📊 Veri Tablosu", command=lambda: self.canvas.set_tool("grid")).pack(side=tk.LEFT, padx=2)

        self.canvas = DesignerCanvas(center_frame, i18n, self.on_component_selected)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=2)

        self.property_sheet = MSTPropertySheet(main_paned, self.db_engine, i18n, self.on_properties_updated)
        main_paned.add(self.property_sheet, weight=3)

        self.root.bind("<F5>", lambda event: self.run_preview())

    def show_page_context_menu(self, event):
        idx = self.pages_listbox.nearest(event.y)
        if idx >= 0:
            self.pages_listbox.selection_clear(0, tk.END)
            self.pages_listbox.selection_set(idx)
            p_name = self.pages_listbox.get(idx).replace("📋 ", "")
            self.active_page = p_name
            self.load_page(p_name)
            self.page_context_menu.tk_popup(event.x_root, event.y_root)

    def rename_selected_page(self):
        old_name = self.active_page
        if not old_name: return

        new_name = simpledialog.askstring("Form İsmini Değiştir", f"'{old_name}' için yeni ismi girin:", initialvalue=old_name, parent=self.root)
        if new_name:
            new_name = new_name.strip().replace(" ", "_")
            if new_name and new_name != old_name:
                if new_name in self.pages:
                    messagebox.showerror("Hata", f"'{new_name}' isminde bir form zaten mevcut!")
                    return

                self.pages[new_name] = self.pages.pop(old_name)
                self.page_components[new_name] = self.page_components.pop(old_name)

                for page_name, comps in self.page_components.items():
                    for c in comps:
                        if c.get("target") == old_name:
                            c["target"] = new_name

                self.active_page = new_name
                self.refresh_pages_list()
                self.load_page(new_name)

    def duplicate_selected_page(self):
        old_name = self.active_page
        if not old_name: return

        new_name = f"{old_name}_Kopya"
        import copy
        self.pages[new_name] = copy.deepcopy(self.pages[old_name])
        self.page_components[new_name] = copy.deepcopy(self.page_components.get(old_name, []))

        self.refresh_pages_list()
        self.active_page = new_name
        self.load_page(new_name)

    def delete_selected_page(self):
        old_name = self.active_page
        if not old_name: return

        if len(self.pages) <= 1:
            messagebox.showwarning("Uyarı", "Projeden son kalan formu silemezsiniz!")
            return

        if messagebox.askyesno("Form Silme Onayı", f"'{old_name}' formu silinecektir. Emin misiniz?"):
            self.pages.pop(old_name)
            self.page_components.pop(old_name)
            self.active_page = list(self.pages.keys())[0]
            self.refresh_pages_list()
            self.load_page(self.active_page)

    def add_custom_page(self, page_name, components):
        self.pages[page_name] = {"is_login": False, "role": "Herkes"}
        self.page_components[page_name] = components
        self.refresh_pages_list()
        self.active_page = page_name
        self.load_page(page_name)

    def toggle_theme(self):
        new_theme = self.theme_engine.toggle_theme(self.root)
        canvas_bg = self.theme_engine.colors.get("bg_canvas", "#ffffff")
        self.canvas.canvas.configure(bg=canvas_bg)
        self.canvas.render_all()

    def save_project_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".mst",
            filetypes=[("MST Proje Dosyası", "*.mst"), ("Tüm Dosyalar", "*.*")],
            title="Projeyi .mst Olarak Kaydet"
        )
        if file_path:
            self.project_engine.pages = self.pages
            self.project_engine.page_components = self.page_components
            self.project_engine.save_project(file_path)
            messagebox.showinfo("MST Studio", f"Proje kaydedildi:\n{file_path}")

    def load_mst_file_from_path(self, file_path):
        try:
            self.project_engine.load_project(file_path)
            self.pages = self.project_engine.pages
            self.page_components = self.project_engine.page_components
            self.refresh_pages_list()
            if self.pages:
                self.active_page = list(self.pages.keys())[0]
                self.load_page(self.active_page)
            self.root.title(f"MST Studio - [{os.path.basename(file_path)}]")
        except Exception as e:
            messagebox.showerror("Hata", f"Proje yüklenirken hata oluştu:\n{str(e)}")

    def open_project_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("MST Proje Dosyası", "*.mst"), ("Tüm Dosyalar", "*.*")],
            title="Projeyi Aç"
        )
        if file_path:
            self.load_mst_file_from_path(file_path)

    def refresh_pages_list(self):
        self.pages_listbox.delete(0, tk.END)
        for p in self.pages.keys():
            self.pages_listbox.insert(tk.END, f"📋 {p}")

    def add_page_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Yeni Form Ekle")
        win.geometry("300x120")
        ttk.Label(win, text="Form Adı:").pack(pady=5)
        e_name = ttk.Entry(win, width=25)
        e_name.pack(pady=2)

        def save():
            p = e_name.get().strip().replace(" ", "_")
            if p and p not in self.pages:
                self.pages[p] = {"is_login": False, "role": "Herkes"}
                self.page_components[p] = []
                self.refresh_pages_list()
                win.destroy()

        ttk.Button(win, text="Oluştur", command=save).pack(pady=10)

    def open_packager_dialog(self):
        self.project_engine.pages = self.pages
        self.project_engine.page_components = self.page_components
        MSTPackagerDialog(self.root, self.project_engine, self.db_engine)

    def on_page_select(self, event):
        sel = self.pages_listbox.curselection()
        if sel:
            p_name = self.pages_listbox.get(sel[0]).replace("📋 ", "")
            self.active_page = p_name
            self.load_page(p_name)

    def load_page(self, page_name):
        comps = self.page_components.get(page_name, [])
        self.canvas.load_components(comps)
        self.property_sheet.load_page_properties(page_name, self.pages)

    def on_component_selected(self, comp):
        if comp:
            self.property_sheet.load_component(comp)
        else:
            self.property_sheet.load_page_properties(self.active_page, self.pages)

    def on_properties_updated(self):
        self.canvas.render_all()

    def run_preview(self):
        LiveSimulator(self.root, self.db_engine, i18n, self.pages, self.page_components, self.active_page)

if __name__ == "__main__":
    root = tk.Tk()
    app = MSTStudioIDE(root)
    root.mainloop()

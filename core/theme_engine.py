#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from tkinter import ttk

class MSTThemeEngine:
    """IDE ve Canlı Çalıştırıcı için dinamik Light/Dark Tema Yöneticisi."""

    def __init__(self, themes_dir="assets/themes"):
        self.themes_dir = themes_dir
        self.current_theme_name = "light"
        self.colors = {}
        self.load_theme("light")

    def load_theme(self, theme_name):
        path = os.path.join(self.themes_dir, f"{theme_name}.json")
        if not os.path.exists(path):
            theme_name = "light"
            path = os.path.join(self.themes_dir, "light.json")

        with open(path, "r", encoding="utf-8") as f:
            self.colors = json.load(f)

        self.current_theme_name = theme_name
        return self.colors

    def apply_theme_to_root(self, root):
        """Tkinter ttk stillerini yüklenen tema renk haritasına uyarlar."""
        style = ttk.Style(root)
        style.theme_use("clam")

        c = self.colors
        bg_main = c.get("bg_main", "#f0f0f0")
        bg_panel = c.get("bg_panel", "#ffffff")
        fg_text = c.get("fg_text", "#222222")
        border = c.get("border_color", "#cccccc")
        accent = c.get("accent_color", "#007acc")

        root.configure(bg=bg_main)

        style.configure(".", background=bg_main, foreground=fg_text, bordercolor=border)
        style.configure("TFrame", background=bg_main)
        style.configure("TLabelframe", background=bg_panel, foreground=fg_text, bordercolor=border)
        style.configure("TLabelframe.Label", background=bg_panel, foreground=accent, font=("Helvetica", 9, "bold"))
        style.configure("TButton", background=bg_panel, foreground=fg_text, bordercolor=border, padding=4)
        style.map("TButton", background=[("active", accent)], foreground=[("active", "#ffffff")])
        style.configure("TEntry", fieldbackground=bg_panel, foreground=fg_text)
        style.configure("TCombobox", fieldbackground=bg_panel, foreground=fg_text)
        style.configure("Treeview", background=bg_panel, foreground=fg_text, fieldbackground=bg_panel)
        style.map("Treeview", background=[("selected", accent)], foreground=[("selected", "#ffffff")])

    def toggle_theme(self, root):
        new_theme = "dark" if self.current_theme_name == "light" else "light"
        self.load_theme(new_theme)
        self.apply_theme_to_root(root)
        return new_theme

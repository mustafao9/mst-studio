#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, Menu

class DesignerCanvas(ttk.Frame):
    def __init__(self, parent, i18n_engine, on_select_cb=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.i18n = i18n_engine
        self.on_select_cb = on_select_cb

        self.components = []
        self.selected_component = None
        self.selected_components = []
        self.grid_size = 10
        self.current_tool = "select"
        self.active_drag_field = None
        self.drag_ghost_coords = None

        self.setup_ui()
        self.setup_context_menu()

    def setup_ui(self):
        self.canvas = tk.Canvas(self, bg="#ffffff", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-3>", self.show_context_menu)

    def setup_context_menu(self):
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="⚙️ Özellikleri Düzenle", command=self.open_properties)
        self.context_menu.add_command(label="📋 Kopyala", command=self.duplicate_component)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Elemanı Sil", command=self.delete_selected)

    def start_drag_field(self, field_data):
        self.active_drag_field = field_data

    def update_drag_ghost(self, x, y):
        if self.active_drag_field:
            self.drag_ghost_coords = (self.snap_to_grid(x), self.snap_to_grid(y))
            self.render_all()

    def show_context_menu(self, event):
        comp = self.find_component_at(event.x, event.y)
        if comp:
            self.selected_component = comp
            if self.on_select_cb:
                self.on_select_cb(comp)
            self.render_all()
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def open_properties(self):
        if self.on_select_cb and self.selected_component:
            self.on_select_cb(self.selected_component)

    def duplicate_component(self):
        if self.selected_component:
            import copy
            new_comp = copy.deepcopy(self.selected_component)
            new_comp["id"] = max([c["id"] for c in self.components], default=0) + 1
            new_comp["x"] += 20
            new_comp["y"] += 20
            self.components.append(new_comp)
            self.selected_component = new_comp
            self.render_all()

    def set_tool(self, tool_name):
        self.current_tool = tool_name

    def load_components(self, components_list):
        self.components = components_list
        self.selected_component = None
        self.selected_components = []
        self.render_all()

    def snap_to_grid(self, val):
        return round(val / self.grid_size) * self.grid_size

    def find_component_at(self, x, y):
        for c in reversed(self.components):
            if c['x'] <= x <= c['x'] + c['w'] and c['y'] <= y <= c['y'] + c['h']:
                return c
        return None

    def on_canvas_click(self, event):
        x, y = self.snap_to_grid(event.x), self.snap_to_grid(event.y)

        if self.current_tool != "select":
            comp_type_map = {
                "label": "Etiket",
                "input": "Metin Kutusu",
                "checkbox": "Onay Kutusu",
                "button": "Buton",
                "grid": "Veri Tablosu"
            }
            c_type = comp_type_map.get(self.current_tool, "Etiket")
            new_id = max([c["id"] for c in self.components], default=0) + 1
            
            new_comp = {
                "id": new_id,
                "type": c_type,
                "x": x, "y": y,
                "w": 180 if c_type == "Veri Tablosu" else 120,
                "h": 120 if c_type == "Veri Tablosu" else 30,
                "text": f"{c_type}_{new_id}",
                "table": "", "field": ""
            }
            self.components.append(new_comp)
            self.selected_component = new_comp
            self.current_tool = "select"
            self.render_all()
            if self.on_select_cb:
                self.on_select_cb(new_comp)
            return

        comp = self.find_component_at(event.x, event.y)
        self.selected_component = comp
        self.render_all()

        if self.on_select_cb:
            self.on_select_cb(comp)

    def on_canvas_drag(self, event):
        if self.selected_component:
            self.selected_component['x'] = self.snap_to_grid(event.x)
            self.selected_component['y'] = self.snap_to_grid(event.y)
            self.render_all()

    def on_canvas_release(self, event):
        # Sol ağaçtan tuvale bırakma tespiti
        if self.active_drag_field and self.drag_ghost_coords:
            gx, gy = self.drag_ghost_coords
            tbl = self.active_drag_field["table"]
            fld = self.active_drag_field["field"]

            lbl_id = max([c["id"] for c in self.components], default=0) + 1
            input_id = lbl_id + 1

            # Sütun Tipine Göre Eleman Kararı (Sehir/Kategori ise Açılır Liste)
            is_lookup = ("sehir" in fld.lower() or "kategori" in fld.lower() or "rol" in fld.lower())
            input_type = "Açılır Liste" if is_lookup else "Metin Kutusu"

            # 1. Etiket Nesnesi
            lbl_comp = {
                "id": lbl_id,
                "type": "Etiket",
                "x": gx, "y": gy,
                "w": 100, "h": 25,
                "text": f"{fld.title().replace('_', ' ')}:",
                "table": "", "field": ""
            }

            # 2. Bağlı Giriş Kutusu Nesnesi
            input_comp = {
                "id": input_id,
                "type": input_type,
                "x": gx + 110, "y": gy,
                "w": 160, "h": 28,
                "text": "",
                "table": tbl,
                "field": fld
            }

            self.components.extend([lbl_comp, input_comp])
            self.selected_component = input_comp

            self.active_drag_field = None
            self.drag_ghost_coords = None
            self.render_all()

            if self.on_select_cb:
                self.on_select_cb(input_comp)

    def delete_selected(self):
        if self.selected_component in self.components:
            self.components.remove(self.selected_component)
            self.selected_component = None
            self.render_all()
            if self.on_select_cb:
                self.on_select_cb(None)

    def draw_grid(self):
        w = self.canvas.winfo_width() or 1000
        h = self.canvas.winfo_height() or 800
        for x in range(0, w, self.grid_size):
            self.canvas.create_line(x, 0, x, h, fill="#f0f0f0")
        for y in range(0, h, self.grid_size):
            self.canvas.create_line(0, y, w, y, fill="#f0f0f0")

    def render_all(self):
        self.canvas.delete("all")
        self.draw_grid()

        for c in self.components:
            x, y, w, h = c['x'], c['y'], c['w'], c['h']
            is_sel = (c == self.selected_component)
            outline_color = "#007acc" if is_sel else "#aaaaaa"
            width = 2 if is_sel else 1

            self.canvas.create_rectangle(x, y, x + w, y + h, outline=outline_color, width=width, fill="#ffffff")

            disp_text = c.get('text', '')
            if c.get('table') and c.get('field'):
                disp_text = f"[{c['field']}]"

            self.canvas.create_text(x + 10, y + h/2, text=f"❖ {c['type']}: {disp_text}", anchor="w", font=("Helvetica", 9))

        # Sürükleme Hayalet Çerçevesi (Drag Ghost)
        if self.active_drag_field and self.drag_ghost_coords:
            gx, gy = self.drag_ghost_coords
            self.canvas.create_rectangle(gx, gy, gx + 270, gy + 30, outline="#2eb85c", width=2, dash=(4, 4))
            self.canvas.create_text(gx + 10, gy + 15, text=f"➕ Ekle: {self.active_drag_field['table']}.{self.active_drag_field['field']}", anchor="w", fill="#2eb85c", font=("Helvetica", 9, "bold"))

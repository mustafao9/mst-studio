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

        # Çoklu Seçim ve Hizalama Kılavuzu Değişkenleri
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.selection_box = None
        self.smart_guides = []  # [(x1, y1, x2, y2, color), ...]

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
            if comp not in self.selected_components:
                self.selected_components = [comp]
            self.selected_component = comp
            if self.on_select_cb:
                self.on_select_cb(comp)
            self.render_all()
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def open_properties(self):
        if self.on_select_cb and self.selected_component:
            self.on_select_cb(self.selected_component)

    def duplicate_component(self):
        if self.selected_components:
            import copy
            new_selection = []
            for comp in self.selected_components:
                new_comp = copy.deepcopy(comp)
                new_comp["id"] = max([c["id"] for c in self.components], default=0) + 1
                new_comp["x"] += 20
                new_comp["y"] += 20
                self.components.append(new_comp)
                new_selection.append(new_comp)
            self.selected_components = new_selection
            self.selected_component = new_selection[0] if new_selection else None
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

    def calculate_smart_guides(self, moving_comp):
        """Taşınan bileşen ile diğer tüm bileşenler arasında hiza çizgilerini hesaplar."""
        self.smart_guides = []
        if not moving_comp:
            return

        mx, my, mw, mh = moving_comp['x'], moving_comp['y'], moving_comp['w'], moving_comp['h']
        mc_x = mx + mw / 2
        mc_y = my + mh / 2

        threshold = 5  # Yakalama hassasiyeti (piksel)

        for other in self.components:
            if other == moving_comp or other in self.selected_components:
                continue

            ox, oy, ow, oh = other['x'], other['y'], other['w'], other['h']
            oc_x = ox + ow / 2
            oc_y = oy + oh / 2

            # Dikey Hizalamalar (Sol, Merkez, Sağ)
            if abs(mx - ox) <= threshold:  # Sol Kenar
                self.smart_guides.append((ox, 0, ox, 1000, "#ff0055"))
            if abs(mc_x - oc_x) <= threshold:  # Dikey Merkez
                self.smart_guides.append((oc_x, 0, oc_x, 1000, "#00aaff"))
            if abs((mx + mw) - (ox + ow)) <= threshold:  # Sağ Kenar
                self.smart_guides.append((ox + ow, 0, ox + ow, 1000, "#ff0055"))

            # Yatay Hizalamalar (Üst, Merkez, Alt)
            if abs(my - oy) <= threshold:  # Üst Kenar
                self.smart_guides.append((0, oy, 1200, oy, "#ff0055"))
            if abs(mc_y - oc_y) <= threshold:  # Yatay Merkez
                self.smart_guides.append((0, oc_y, 1200, oc_y, "#00aaff"))
            if abs((my + mh) - (oy + oh)) <= threshold:  # Alt Kenar
                self.smart_guides.append((0, oy + oh, 1200, oy + oh, "#ff0055"))

    def on_canvas_click(self, event):
        x, y = self.snap_to_grid(event.x), self.snap_to_grid(event.y)
        self.drag_start_x = event.x
        self.drag_start_y = event.y

        # Araç çubuğundan eleman ekleme
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
            self.selected_components = [new_comp]
            self.selected_component = new_comp
            self.current_tool = "select"
            self.render_all()
            if self.on_select_cb:
                self.on_select_cb(new_comp)
            return

        comp = self.find_component_at(event.x, event.y)
        shift_pressed = (event.state & 0x0001) != 0  # Shift tuşu kontrolü

        if comp:
            if shift_pressed:
                if comp in self.selected_components:
                    self.selected_components.remove(comp)
                else:
                    self.selected_components.append(comp)
            else:
                if comp not in self.selected_components:
                    self.selected_components = [comp]
            self.selected_component = comp
        else:
            if not shift_pressed:
                self.selected_components = []
                self.selected_component = None

        self.render_all()
        if self.on_select_cb:
            self.on_select_cb(self.selected_component)

    def on_canvas_drag(self, event):
        if self.selected_components and self.current_tool == "select":
            dx = self.snap_to_grid(event.x) - self.snap_to_grid(self.drag_start_x)
            dy = self.snap_to_grid(event.y) - self.snap_to_grid(self.drag_start_y)

            if dx != 0 or dy != 0:
                for c in self.selected_components:
                    c['x'] += dx
                    c['y'] += dy

                self.drag_start_x = event.x
                self.drag_start_y = event.y

                # Akıllı Hizalama Çizgilerini Hesapla (Grup içindeki ilk elemana göre)
                self.calculate_smart_guides(self.selected_components[0])
                self.render_all()

        elif not self.selected_components:  # Boş alanda Seçim Çerçevesi Açma (Rubber-Band Box)
            self.selection_box = (
                min(self.drag_start_x, event.x),
                min(self.drag_start_y, event.y),
                max(self.drag_start_x, event.x),
                max(self.drag_start_y, event.y)
            )
            # Seçim kutusu içine giren bileşenleri tespit et
            x1, y1, x2, y2 = self.selection_box
            self.selected_components = [
                c for c in self.components 
                if (x1 <= c['x'] + c['w'] and c['x'] <= x2 and y1 <= c['y'] + c['h'] and c['y'] <= y2)
            ]
            self.selected_component = self.selected_components[0] if self.selected_components else None
            self.render_all()

    def on_canvas_release(self, event):
        self.smart_guides = []
        self.selection_box = None

        # Sol ağaçtan tuvale bırakma tespiti
        if self.active_drag_field and self.drag_ghost_coords:
            gx, gy = self.drag_ghost_coords
            tbl = self.active_drag_field["table"]
            fld = self.active_drag_field["field"]

            lbl_id = max([c["id"] for c in self.components], default=0) + 1
            input_id = lbl_id + 1

            is_lookup = ("sehir" in fld.lower() or "kategori" in fld.lower() or "rol" in fld.lower())
            input_type = "Açılır Liste" if is_lookup else "Metin Kutusu"

            lbl_comp = {
                "id": lbl_id,
                "type": "Etiket",
                "x": gx, "y": gy,
                "w": 100, "h": 25,
                "text": f"{fld.title().replace('_', ' ')}:",
                "table": "", "field": ""
            }

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
            self.selected_components = [input_comp]
            self.selected_component = input_comp

            self.active_drag_field = None
            self.drag_ghost_coords = None

            if self.on_select_cb:
                self.on_select_cb(input_comp)

        self.render_all()

    def delete_selected(self):
        if self.selected_components:
            for c in self.selected_components:
                if c in self.components:
                    self.components.remove(c)
            self.selected_components = []
            self.selected_component = None
            self.render_all()
            if self.on_select_cb:
                self.on_select_cb(None)

    def draw_grid(self):
        w = self.canvas.winfo_width() or 1000
        h = self.canvas.winfo_height() or 800
        for x in range(0, w, self.grid_size):
            self.canvas.create_line(x, 0, x, h, fill="#f4f4f4")
        for y in range(0, h, self.grid_size):
            self.canvas.create_line(0, y, w, y, fill="#f4f4f4")

    def render_all(self):
        self.canvas.delete("all")
        self.draw_grid()

        # 1. Dinamik Akıllı Hizalama Çizgilerini Çiz
        for x1, y1, x2, y2, color in self.smart_guides:
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=1, dash=(4, 2))

        # 2. Bileşenleri Çiz
        for c in self.components:
            x, y, w, h = c['x'], c['y'], c['w'], c['h']
            is_sel = (c in self.selected_components)
            outline_color = "#007acc" if is_sel else "#bbbbbb"
            width = 2 if is_sel else 1

            self.canvas.create_rectangle(x, y, x + w, y + h, outline=outline_color, width=width, fill="#ffffff")

            # Çoklu seçimde köşe tutamaçları (Handles)
            if is_sel:
                handle_size = 5
                handles = [
                    (x, y), (x + w, y), (x, y + h), (x + w, y + h)
                ]
                for hx, hy in handles:
                    self.canvas.create_rectangle(
                        hx - handle_size/2, hy - handle_size/2,
                        hx + handle_size/2, hy + handle_size/2,
                        fill="#007acc", outline="#ffffff"
                    )

            disp_text = c.get('text', '')
            if c.get('table') and c.get('field'):
                disp_text = f"[{c['field']}]"

            self.canvas.create_text(x + 10, y + h/2, text=f"❖ {c['type']}: {disp_text}", anchor="w", font=("Helvetica", 9))

        # 3. Seçim Çerçevesi (Rubber-Band Box) Çizimi
        if self.selection_box:
            x1, y1, x2, y2 = self.selection_box
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="#007acc", fill="#007acc", stipple="gray25", width=1)

        # 4. Sürükleme Hayalet Çerçevesi (Drag Ghost)
        if self.active_drag_field and self.drag_ghost_coords:
            gx, gy = self.drag_ghost_coords
            self.canvas.create_rectangle(gx, gy, gx + 270, gy + 30, outline="#2eb85c", width=2, dash=(4, 4))
            self.canvas.create_text(gx + 10, gy + 15, text=f"➕ Ekle: {self.active_drag_field['table']}.{self.active_drag_field['field']}", anchor="w", fill="#2eb85c", font=("Helvetica", 9, "bold"))

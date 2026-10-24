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

        self.drag_start_x = 0
        self.drag_start_y = 0
        self.selection_box = None
        self.smart_guides = []
        self.is_box_selecting = False
        self.resizing_handle = None

        self.setup_ui()
        self.setup_context_menu()

    def setup_ui(self):
        self.canvas = tk.Canvas(self, bg="#ffffff", highlightthickness=1, highlightbackground="#d1d5db")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Button-3>", self.show_context_menu)

    def setup_context_menu(self):
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="⚙️ Özellikler Paneli", command=self.open_properties)
        self.context_menu.add_separator()
        
        align_menu = Menu(self.context_menu, tearoff=0)
        align_menu.add_command(label="⇤ Sola Hizala", command=lambda: self.align_selected("left"))
        align_menu.add_command(label="⇥ Sağa Hizala", command=lambda: self.align_selected("right"))
        align_menu.add_command(label="⇡ Üste Hizala", command=lambda: self.align_selected("top"))
        align_menu.add_command(label="⇣ Alta Hizala", command=lambda: self.align_selected("bottom"))
        align_menu.add_separator()
        align_menu.add_command(label="↔ Genişlikleri Eşitle", command=lambda: self.size_selected("width_max"))
        align_menu.add_command(label="↕ Dikeyde Eşit Dağıt", command=self.distribute_vertically)
        self.context_menu.add_cascade(label="📐 Hizala, Eşitle & Dağıt", menu=align_menu)

        layer_menu = Menu(self.context_menu, tearoff=0)
        layer_menu.add_command(label="⬆️ En Öne Getir", command=self.bring_to_front)
        layer_menu.add_command(label="⬇️ En Arkaya Gönder", command=self.send_to_back)
        self.context_menu.add_cascade(label="📑 Katman Sıralaması", menu=layer_menu)

        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔒 Konumu Kilitle / Aç", command=self.toggle_lock)
        self.context_menu.add_command(label="📋 Toplu Çoğalt", command=self.duplicate_component)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Seçilenleri Sil", command=self.delete_selected)

    def align_selected(self, mode):
        if len(self.selected_components) < 2: return
        movable = [c for c in self.selected_components if not c.get('locked', False)]
        if not movable: return

        if mode == "left":
            labels = [c for c in movable if c['type'] == "Etiket"]
            inputs = [c for c in movable if c['type'] != "Etiket"]

            if labels:
                min_label_x = min(c['x'] for c in labels)
                for c in labels: c['x'] = min_label_x

            if inputs:
                min_input_x = min(c['x'] for c in inputs)
                for c in inputs: c['x'] = min_input_x

        elif mode == "top":
            min_y = min(c['y'] for c in movable)
            for c in movable: c['y'] = min_y

        self.render_all()

    def size_selected(self, mode):
        if len(self.selected_components) < 2: return
        movable = [c for c in self.selected_components if not c.get('locked', False)]
        if not movable: return

        if mode == "width_max":
            max_w = max(c['w'] for c in movable)
            for c in movable: c['w'] = max_w

        self.render_all()

    def distribute_vertically(self):
        if len(self.selected_components) < 3: return
        sorted_comps = sorted(self.selected_components, key=lambda c: c['y'])
        first_y = sorted_comps[0]['y']
        last_y = sorted_comps[-1]['y']
        total_h = sum(c['h'] for c in sorted_comps[:-1])
        gap = (last_y - first_y - total_h) / (len(sorted_comps) - 1)
        curr_y = first_y
        for c in sorted_comps:
            c['y'] = self.snap_to_grid(curr_y)
            curr_y += c['h'] + gap
        self.render_all()

    def bring_to_front(self):
        for c in self.selected_components:
            if c in self.components:
                self.components.remove(c)
                self.components.append(c)
        self.render_all()

    def send_to_back(self):
        for c in reversed(self.selected_components):
            if c in self.components:
                self.components.remove(c)
                self.components.insert(0, c)
        self.render_all()

    def toggle_lock(self):
        for c in self.selected_components:
            c['locked'] = not c.get('locked', False)
        self.render_all()

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

    def get_handle_at(self, comp, x, y):
        if not comp: return None
        cx, cy, cw, ch = comp['x'], comp['y'], comp['w'], comp['h']
        h_size = 6
        if (cx + cw - h_size <= x <= cx + cw + h_size) and (cy + ch/2 - h_size <= y <= cy + ch/2 + h_size):
            return 'e'
        if (cx + cw/2 - h_size <= x <= cx + cw/2 + h_size) and (cy + ch - h_size <= y <= cy + ch + h_size):
            return 's'
        if (cx + cw - h_size <= x <= cx + cw + h_size) and (cy + ch - h_size <= y <= cy + ch + h_size):
            return 'se'
        return None

    def find_component_at(self, x, y):
        for c in reversed(self.components):
            if c['x'] <= x <= c['x'] + c['w'] and c['y'] <= y <= c['y'] + c['h']:
                return c
        return None

    def on_canvas_click(self, event):
        x, y = self.snap_to_grid(event.x), self.snap_to_grid(event.y)
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.resizing_handle = None

        if self.selected_component:
            handle = self.get_handle_at(self.selected_component, event.x, event.y)
            if handle:
                self.resizing_handle = handle
                return

        # Tıklanan Araç Tipi Eşleme (subform ve combo tam eklendi)
        if self.current_tool != "select":
            comp_type_map = {
                "label": "Etiket",
                "input": "Metin Kutusu",
                "combo": "Açılır Liste",
                "checkbox": "Onay Kutusu",
                "button": "Buton",
                "grid": "Veri Tablosu",
                "subform": "Alt Form (Master-Detail)"
            }
            c_type = comp_type_map.get(self.current_tool, "Etiket")
            new_id = max([c["id"] for c in self.components], default=0) + 1
            
            new_comp = {
                "id": new_id,
                "type": c_type,
                "x": x, "y": y,
                "w": 340 if c_type in ["Veri Tablosu", "Alt Form (Master-Detail)"] else 130,
                "h": 160 if c_type in ["Veri Tablosu", "Alt Form (Master-Detail)"] else 30,
                "text": f"{c_type}_{new_id}",
                "table": "", "field": "",
                "master_field": "id",
                "detail_field": "",
                "locked": False,
                "pair_id": None
            }
            self.components.append(new_comp)
            self.selected_components = [new_comp]
            self.selected_component = new_comp
            # Eleman çizildikten sonra otomatik olarak "Seç & Taş" moduna geri dön
            self.current_tool = "select"
            self.is_box_selecting = False
            self.render_all()
            if self.on_select_cb:
                self.on_select_cb(new_comp)
            return

        comp = self.find_component_at(event.x, event.y)
        shift_pressed = (event.state & 0x0001) != 0

        if comp:
            self.is_box_selecting = False
            if shift_pressed:
                if comp in self.selected_components:
                    self.selected_components.remove(comp)
                else:
                    self.selected_components.append(comp)
            else:
                pair = [c for c in self.components if c.get('id') == comp.get('pair_id')] if comp.get('pair_id') else []
                if comp not in self.selected_components:
                    self.selected_components = [comp] + pair
            self.selected_component = comp
        else:
            self.is_box_selecting = True
            if not shift_pressed:
                self.selected_components = []
                self.selected_component = None

        self.render_all()
        if self.on_select_cb:
            self.on_select_cb(self.selected_component)

    def on_canvas_drag(self, event):
        if self.resizing_handle and self.selected_component:
            comp = self.selected_component
            new_x = self.snap_to_grid(event.x)
            new_y = self.snap_to_grid(event.y)

            if 'e' in self.resizing_handle:
                comp['w'] = max(30, new_x - comp['x'])
            if 's' in self.resizing_handle:
                comp['h'] = max(20, new_y - comp['y'])

            self.render_all()
            if self.on_select_cb:
                self.on_select_cb(comp)
            return

        if self.is_box_selecting:
            self.selection_box = (
                min(self.drag_start_x, event.x),
                min(self.drag_start_y, event.y),
                max(self.drag_start_x, event.x),
                max(self.drag_start_y, event.y)
            )
            x1, y1, x2, y2 = self.selection_box
            self.selected_components = [
                c for c in self.components 
                if (x1 <= c['x'] + c['w'] and c['x'] <= x2 and y1 <= c['y'] + c['h'] and c['y'] <= y2)
            ]
            self.selected_component = self.selected_components[0] if self.selected_components else None
            self.render_all()

        elif self.selected_components and self.current_tool == "select":
            dx = self.snap_to_grid(event.x) - self.snap_to_grid(self.drag_start_x)
            dy = self.snap_to_grid(event.y) - self.snap_to_grid(self.drag_start_y)

            if dx != 0 or dy != 0:
                movable_comps = [c for c in self.selected_components if not c.get('locked', False)]
                for c in movable_comps:
                    c['x'] += dx
                    c['y'] += dy

                self.drag_start_x = event.x
                self.drag_start_y = event.y

                self.render_all()

    def on_canvas_release(self, event):
        self.smart_guides = []
        self.selection_box = None
        self.is_box_selecting = False
        self.resizing_handle = None

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
                "table": "", "field": "",
                "locked": False,
                "pair_id": input_id
            }

            input_comp = {
                "id": input_id,
                "type": input_type,
                "x": gx + 110, "y": gy,
                "w": 160, "h": 28,
                "text": "",
                "table": tbl,
                "field": fld,
                "locked": False,
                "pair_id": lbl_id
            }

            self.components.extend([lbl_comp, input_comp])
            self.selected_components = [lbl_comp, input_comp]
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

        for c in self.components:
            x, y, w, h = c['x'], c['y'], c['w'], c['h']
            is_sel = (c in self.selected_components)
            is_locked = c.get('locked', False)

            outline_color = "#e55353" if is_locked else ("#007acc" if is_sel else "#d1d5db")
            width = 2 if is_sel else 1

            self.canvas.create_rectangle(x, y, x + w, y + h, outline=outline_color, width=width, fill="#ffffff")

            if c == self.selected_component and not is_locked:
                h_size = 4
                self.canvas.create_rectangle(x + w - h_size, y + h/2 - h_size, x + w + h_size, y + h/2 + h_size, fill="#007acc", outline="#ffffff")
                self.canvas.create_rectangle(x + w/2 - h_size, y + h - h_size, x + w/2 + h_size, y + h + h_size, fill="#007acc", outline="#ffffff")
                self.canvas.create_rectangle(x + w - h_size, y + h - h_size, x + w + h_size, y + h + h_size, fill="#007acc", outline="#ffffff")

            disp_text = c.get('text', '')
            if c['type'] == "Alt Form (Master-Detail)":
                disp_text = f"🔗 Alt Form: [{c.get('table', 'Tablo Seçilmedi')}]"
            elif c.get('table') and c.get('field'):
                disp_text = f"[{c['field']}]"

            lock_icon = "🔒 " if is_locked else ""
            self.canvas.create_text(x + 10, y + h/2, text=f"{lock_icon}❖ {c['type']}: {disp_text}", anchor="w", font=("Helvetica", 9))

        if self.selection_box:
            x1, y1, x2, y2 = self.selection_box
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="#007acc", fill="#007acc", stipple="gray25", width=1)

        if self.active_drag_field and self.drag_ghost_coords:
            gx, gy = self.drag_ghost_coords
            self.canvas.create_rectangle(gx, gy, gx + 270, gy + 30, outline="#2eb85c", width=2, dash=(4, 4))
            self.canvas.create_text(gx + 10, gy + 15, text=f"➕ Ekle: {self.active_drag_field['table']}.{self.active_drag_field['field']}", anchor="w", fill="#2eb85c", font=("Helvetica", 9, "bold"))

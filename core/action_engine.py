#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import messagebox, filedialog
from core.security_engine import SecurityEngine
from core.report_engine import MSTReportEngine

class MSTActionEngine:
    def __init__(self, db_engine, live_simulator_ref):
        self.db = db_engine
        self.simulator = live_simulator_ref
        self.report_engine = MSTReportEngine(db_engine)

    def execute_chain(self, action_chain, inputs_map, page_comps, page_name):
        for step in action_chain:
            act_type = step.get("type")

            if act_type == "validate_inputs":
                if not self.simulator.validate_inputs(page_comps, inputs_map):
                    return False

            elif act_type == "save_or_update_record":
                flds, vals, tbl = [], [], None
                for fld, (e_obj, t_name) in inputs_map.items():
                    val = e_obj.get() if hasattr(e_obj, 'get') else ""
                    if val:
                        if fld.lower() in ["sifre", "password"]:
                            val = SecurityEngine.hash_password(str(val).strip())
                        else:
                            val = str(val).strip()

                        flds.append(fld)
                        vals.append(val)
                        tbl = t_name

                if tbl and flds:
                    row_id = self.simulator.selected_row_id
                    
                    if row_id:
                        # UPDATE İŞLEMİ
                        set_clause = ", ".join([f"{self.db.sanitize(f)} = ?" for f in flds])
                        sql = f"UPDATE {self.db.sanitize(tbl)} SET {set_clause} WHERE id = ?"
                        vals.append(row_id)
                        self.db.execute_query(sql, vals)
                        messagebox.showinfo("Başarılı", f"Kayıt (ID: {row_id}) başarıyla güncellendi!")
                    else:
                        # INSERT İŞLEMİ
                        qmarks = ", ".join(["?"] * len(vals))
                        sql = f"INSERT INTO {self.db.sanitize(tbl)} ({', '.join(flds)}) VALUES ({qmarks})"
                        self.db.execute_query(sql, vals)
                        messagebox.showinfo("Başarılı", "Yeni kayıt başarıyla eklendi!")

                    # Sayfayı ve Grid'leri Yenile
                    self.simulator.render_page(page_name)

            elif act_type == "export_report":
                tbl = step.get("table", "kullanicilar")
                fmt = step.get("format", "csv")
                
                if fmt == "csv":
                    out_file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Dosyası", "*.csv")], title="Raporu CSV Olarak Kaydet")
                    if out_file:
                        self.report_engine.export_to_csv(tbl, out_file)
                        messagebox.showinfo("Başarılı", f"Rapor CSV olarak kaydedildi:\n{out_file}")
                elif fmt == "html":
                    out_file = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Rapor", "*.html")], title="Raporu HTML Olarak Kaydet")
                    if out_file:
                        self.report_engine.export_to_html(tbl, out_file, title=f"{tbl.upper()} Tablo Raporu")
                        messagebox.showinfo("Başarılı", f"Rapor HTML olarak kaydedildi:\n{out_file}")

            elif act_type == "show_message":
                msg_text = step.get("text", "İşlem başarıyla gerçekleştirildi.")
                messagebox.showinfo("MST Studio", msg_text)

            elif act_type == "navigate":
                target_page = step.get("target")
                if target_page:
                    self.simulator.render_page(target_page)
                    return True

        return True

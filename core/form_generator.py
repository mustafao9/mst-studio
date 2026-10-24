#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class MSTFormGenerator:
    """Veritabanı tablosunun şemasını analiz ederek tuval için otomatik hizalı form bileşenleri üreten motor."""

    @classmethod
    def generate_form_for_table(cls, table_name, columns_info):
        components = []
        comp_id = 1

        # Form Başlığı
        components.append({
            "id": comp_id,
            "type": "Etiket",
            "x": 40, "y": 30, "w": 320, "h": 30,
            "text": f"📋 {table_name.upper()} YÖNETİM FORMU",
            "table": "", "field": ""
        })
        comp_id += 1

        start_y = 80
        y_gap = 40
        current_y = start_y

        for col in columns_info:
            c_name = col['name']
            if c_name.lower() == 'id':
                continue

            disp_label = c_name.replace("_", " ").title() + ":"

            # Etiket
            components.append({
                "id": comp_id,
                "type": "Etiket",
                "x": 40, "y": current_y, "w": 110, "h": 28,
                "text": disp_label,
                "table": "", "field": ""
            })
            comp_id += 1

            # Veri Tipi / Isim Analizi
            if "SEHIR" in c_name.upper() or "ROL" in c_name.upper() or "KATEGORI" in c_name.upper():
                comp_type = "Açılır Liste"
            else:
                comp_type = "Metin Kutusu"

            comp_dict = {
                "id": comp_id,
                "type": comp_type,
                "x": 160, "y": current_y, "w": 220, "h": 28,
                "text": "",
                "table": table_name,
                "field": c_name,
                "is_required": True if "ad" in c_name.lower() else False,
                "validation_rule": "Yok",
                "validation_msg": f"{disp_label} alanı zorunludur!"
            }

            if comp_type == "Açılır Liste":
                comp_dict["options"] = "Seçenek 1, Seçenek 2, Seçenek 3"
                comp_dict["lookup_table"] = ""
                comp_dict["lookup_field"] = ""

            components.append(comp_dict)
            comp_id += 1
            current_y += y_gap

        btn_y = current_y + 10

        # Kaydet Butonu
        components.append({
            "id": comp_id,
            "type": "Buton",
            "x": 160, "y": btn_y, "w": 120, "h": 32,
            "text": "💾 Kaydet",
            "action": "Kayıt Ekle",
            "target": ""
        })
        comp_id += 1

        # Veri Tablosu (Grid View)
        components.append({
            "id": comp_id,
            "type": "Veri Tablosu",
            "x": 410, "y": start_y, "w": 450, "h": max(260, (current_y - start_y) + 40),
            "table": table_name,
            "field": ""
        })

        return components

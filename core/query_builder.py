#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class MSTQueryBuilder:
    """Tabloları, JOIN ilişkilerini ve hesaplanmış sütunları görsel parametrelerle SQL cümlesine dönüştüren motor."""

    def __init__(self, main_table):
        self.main_table = main_table
        self.joins = [] # [{'type': 'INNER', 'table': 'sehirler', 'left_col': 'musteriler.sehir_id', 'right_col': 'sehirler.id'}]
        self.selected_columns = [] # [{'table': 'musteriler', 'column': 'ad_soyad', 'alias': 'Müşteri Adı'}]
        self.calculated_columns = [] # [{'expression': 'fiyat * adet', 'alias': 'Toplam Tutar'}]
        self.where_conditions = [] # [{'column': 'yas', 'operator': '>=', 'value': '18'}]

    def add_join(self, join_type, target_table, left_col, right_col):
        self.joins.append({
            'type': join_type.upper(),
            'table': target_table,
            'left_col': left_col,
            'right_col': right_col
        })

    def add_column(self, table, column, alias=""):
        self.selected_columns.append({
            'table': table,
            'column': column,
            'alias': alias
        })

    def add_calculated_column(self, expression, alias):
        self.calculated_columns.append({
            'expression': expression,
            'alias': alias
        })

    def add_where(self, column, operator, value):
        self.where_conditions.append({
            'column': column,
            'operator': operator,
            'value': value
        })

    def build_sql(self):
        # 1. SELECT Sütunları
        cols_sql = []
        for c in self.selected_columns:
            col_str = f"{c['table']}.{c['column']}"
            if c.get('alias'):
                col_str += f" AS [{c['alias']}]"
            cols_sql.append(col_str)

        for calc in self.calculated_columns:
            calc_str = f"({calc['expression']}) AS [{calc['alias']}]"
            cols_sql.append(calc_str)

        select_part = ", ".join(cols_sql) if cols_sql else f"{self.main_table}.*"

        # 2. FROM ve JOIN Cümlecikleri
        from_part = f"FROM {self.main_table}"
        joins_sql = []
        for j in self.joins:
            joins_sql.append(f"{j['type']} JOIN {j['table']} ON {j['left_col']} = {j['right_col']}")

        join_part = " ".join(joins_sql)

        # 3. WHERE Koşulları
        where_part = ""
        if self.where_conditions:
            conds = []
            for w in self.where_conditions:
                conds.append(f"{w['column']} {w['operator']} '{w['value']}'")
            where_part = "WHERE " + " AND ".join(conds)

        sql_components = [f"SELECT {select_part}", from_part]
        if join_part:
            sql_components.append(join_part)
        if where_part:
            sql_components.append(where_part)

        return " ".join(sql_components) + ";"

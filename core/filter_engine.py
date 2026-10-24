#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class FilterEngine:
    def __init__(self, db_engine):
        self.db = db_engine

    def build_filter_query(self, table_name, filters):
        """
        table_name: 'urunler'
        filters: [
            {'field': 'urun_adi', 'operator': 'contains', 'value': 'Ekmek'},
            {'field': 'fiyati', 'operator': 'gte', 'value': 10},
            {'field': 'stok', 'operator': 'between', 'value': [10, 100]}
        ]
        """
        sql = f"SELECT * FROM {self.db.sanitize(table_name)}"
        where_clauses = []
        params = []

        for f in filters:
            field = self.db.sanitize(f['field'])
            op = f['operator']
            val = f['value']

            if op == 'equals':
                where_clauses.append(f"{field} = ?")
                params.append(val)
            elif op == 'contains':
                where_clauses.append(f"{field} LIKE ?")
                params.append(f"%{val}%")
            elif op == 'starts_with':
                where_clauses.append(f"{field} LIKE ?")
                params.append(f"{val}%")
            elif op == 'ends_with':
                where_clauses.append(f"{field} LIKE ?")
                params.append(f"%{val}")
            elif op == 'gt':
                where_clauses.append(f"{field} > ?")
                params.append(val)
            elif op == 'gte':
                where_clauses.append(f"{field} >= ?")
                params.append(val)
            elif op == 'lt':
                where_clauses.append(f"{field} < ?")
                params.append(val)
            elif op == 'lte':
                where_clauses.append(f"{field} <= ?")
                params.append(val)
            elif op == 'between' and isinstance(val, (list, tuple)) and len(val) == 2:
                where_clauses.append(f"{field} BETWEEN ? AND ?")
                params.extend(val)

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        return sql, params

    def apply_filter(self, table_name, filters=None):
        if not filters:
            sql = f"SELECT * FROM {self.db.sanitize(table_name)}"
            params = []
        else:
            sql, params = self.build_filter_query(table_name, filters)

        cursor = self.db.execute_query(sql, params)
        return cursor.fetchall()

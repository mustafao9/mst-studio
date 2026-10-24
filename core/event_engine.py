#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class MSTEventEngine:
    """Form ve bileşen yaşam döngüsü olaylarını (Event Hooks & Macros) yöneten çekirdek motor."""

    EVENTS = ["OnLoad", "BeforeInsert", "AfterInsert", "OnChange", "OnClick"]

    def __init__(self, action_engine):
        self.action_engine = action_engine
        self.event_hooks = {} # {'Giris_Sayfasi': {'OnLoad': [chain_steps]}}

    def register_hook(self, page_or_comp, event_type, action_chain):
        """Olay tetikleyicisine bir eylem zinciri bağlar."""
        if event_type not in self.EVENTS:
            raise ValueError(f"Geçersiz olay tipi: {event_type}")

        if page_or_comp not in self.event_hooks:
            self.event_hooks[page_or_comp] = {}

        self.event_hooks[page_or_comp][event_type] = action_chain

    def trigger_event(self, page_or_comp, event_type, inputs_map=None, page_comps=None, page_name=""):
        """Tetiklenen olaya bağlı eylem zincirini çalıştırır."""
        hooks = self.event_hooks.get(page_or_comp, {})
        chain = hooks.get(event_type, [])

        if not chain:
            return True # Bağlı olay yoksa işleme devam et

        inputs_map = inputs_map or {}
        page_comps = page_comps or []

        return self.action_engine.execute_chain(chain, inputs_map, page_comps, page_name)

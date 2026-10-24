#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from unittest.mock import MagicMock
from core.event_engine import MSTEventEngine

class TestMSTEventEngine(unittest.TestCase):
    def setUp(self):
        self.mock_action_engine = MagicMock()
        self.event_engine = MSTEventEngine(self.mock_action_engine)

    def test_register_and_trigger_hook(self):
        chain = [{"type": "show_message", "text": "Form Yüklendi!"}]
        self.event_engine.register_hook("Ana_Sayfa", "OnLoad", chain)

        self.event_engine.trigger_event("Ana_Sayfa", "OnLoad")
        self.mock_action_engine.execute_chain.assert_called_once_with(chain, {}, [], "")

    def test_invalid_event_type(self):
        with self.assertRaises(ValueError):
            self.event_engine.register_hook("Ana_Sayfa", "InvalidEvent", [])

if __name__ == '__main__':
    unittest.main()

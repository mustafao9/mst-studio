#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
from core.security_engine import SecurityEngine

class TestSecurityEngine(unittest.TestCase):
    def test_hash_and_verify(self):
        password = "GüvenliSifre123!"
        hashed = SecurityEngine.hash_password(password)

        # Hash yapısı denetimi
        self.assertIn("$", hashed)
        self.assertNotEqual(password, hashed)

        # Doğru Parola Doğrulaması
        self.assertTrue(SecurityEngine.verify_password(hashed, password))

        # Yanlış Parola Reddi
        self.assertFalse(SecurityEngine.verify_password(hashed, "YanlisSifre"))

if __name__ == '__main__':
    unittest.main()

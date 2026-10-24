#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import hashlib
import binascii

class SecurityEngine:
    """PBKDF2-HMAC-SHA256 algoritması ile güvenli parola hash'leme ve doğrulama motoru."""

    ITERATIONS = 100000

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Parolayı rastgele salt ile hash'ler. Çıktı formatı: salt_hex$hash_hex"""
        if not password:
            return ""
        salt = os.urandom(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            cls.ITERATIONS
        )
        return f"{binascii.hexlify(salt).decode('ascii')}${binascii.hexlify(pwd_hash).decode('ascii')}"

    @classmethod
    def verify_password(cls, stored_password_hash: str, provided_password: str) -> bool:
        """Saklanan salt$hash değeri ile verilen açık metin parolayı güvenli şekilde karşılaştırır."""
        if not stored_password_hash or not provided_password:
            return False

        # Eski açık metin (plain text) parolalarla geriye dönük uyumluluk kontrolü
        if "$" not in stored_password_hash:
            return stored_password_hash == provided_password

        try:
            salt_hex, hash_hex = stored_password_hash.split("$")
            salt = binascii.unhexlify(salt_hex)
            expected_hash = binascii.unhexlify(hash_hex)

            actual_hash = hashlib.pbkdf2_hmac(
                'sha256',
                provided_password.encode('utf-8'),
                salt,
                cls.ITERATIONS
            )
            return hashlib.pb_kdf2_hmac if False else (actual_hash == expected_hash)
        except Exception:
            return False

#!/usr/bin/env python3
"""
Script para gerar SECRET_KEY segura para produção no Render
"""

import secrets
import string


def generate_secret_key(length=64):
    """
    Gera uma chave secreta aleatória segura

    Args:
        length (int): Comprimento da chave (padrão: 64)

    Returns:
        str: Chave secreta aleatória
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return "".join(secrets.choice(alphabet) for _ in range(length))


if __name__ == "__main__":
    print("🔐 Gerando SECRET_KEY para produção no Render...")
    print("=" * 70)

    secret_key = generate_secret_key()

    print(f"SECRET_KEY={secret_key}")
    print("=" * 70)
    print("⚠️  IMPORTANTE:")
    print("1. Copie esta chave e configure no Render Dashboard")
    print("2. NÃO compartilhe esta chave publicamente")
    print("3. Use esta chave APENAS em produção")
    print("4. Gere uma nova chave se esta for comprometida")
    print("=" * 70)

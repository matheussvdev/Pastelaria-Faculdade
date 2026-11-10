
import os
from pathlib import Path

from dotenv import dotenv_values
from supabase import Client, create_client


RAIZ_PROJETO = Path(__file__).resolve().parents[2]
ARQUIVO_ENV = RAIZ_PROJETO / ".env"


def criar_cliente_supabase() -> Client:
    # =========================================
    # 1. CONFIGURAÇÕES DO AMBIENTE
    # =========================================

    configuracoes = {}

    if ARQUIVO_ENV.is_file():
        configuracoes = dotenv_values(ARQUIVO_ENV)

    url = (
        os.getenv("SUPABASE_URL")
        or configuracoes.get("SUPABASE_URL")
    )

    chave = (
        os.getenv("SUPABASE_KEY")
        or configuracoes.get("SUPABASE_KEY")
    )

    # =========================================
    # 2. CONFIGURAÇÕES EMBUTIDAS NO APLICATIVO
    # =========================================

    if not url or not chave:
        from app.supabase_config import (
            SUPABASE_URL,
            SUPABASE_KEY,
        )

        url = url or SUPABASE_URL
        chave = chave or SUPABASE_KEY

    # =========================================
    # 3. VALIDAÇÃO
    # =========================================

    if (
        not url
        or not chave
        or url == "https://zlhnbzashndifhicnuhr.supabase.co"
        or chave == "sb_publishable_5RGOfzXFZgYiTJez9a9kQg_EUJFim4B"
    ):
        raise RuntimeError(
            "As configurações públicas do Supabase "
            "não foram encontradas."
        )

    print("URL do Supabase configurada:", bool(url))
    print("Chave pública configurada:", bool(chave))

    # =========================================
    # 4. CRIAR CLIENTE
    # =========================================

    cliente = create_client(url, chave)

    return cliente

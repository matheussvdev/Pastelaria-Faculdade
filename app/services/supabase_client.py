
import os
from pathlib import Path

from dotenv import dotenv_values
from supabase import Client, create_client


RAIZ_PROJETO = Path(__file__).resolve().parents[2]
ARQUIVO_ENV = RAIZ_PROJETO / ".env"


def criar_cliente_supabase() -> Client:
    configuracoes = {}

    # 1. Carregar configurações locais, se existirem
    if ARQUIVO_ENV.is_file():
        configuracoes = dotenv_values(ARQUIVO_ENV)

    # 2. Priorizar variáveis de ambiente
    url = os.getenv("SUPABASE_URL") or configuracoes.get(
        "SUPABASE_URL"
    )

    chave = os.getenv("SUPABASE_KEY") or configuracoes.get(
        "SUPABASE_KEY"
    )

    # 3. Usar configurações públicas do aplicativo
    # quando não existir arquivo .env (ex.: Android)
    if not url or not chave:
        from app.supabase_public_config import (
            SUPABASE_URL,
            SUPABASE_KEY,
        )

        url = url or SUPABASE_URL
        chave = chave or SUPABASE_KEY

    # 4. Validar configurações
    if not url or not chave:
        raise RuntimeError(
            "As configurações públicas do Supabase "
            "não foram encontradas."
        )

    print("URL do Supabase configurada:", bool(url))
    print("Chave do Supabase configurada:", bool(chave))

    return create_client(url, chave)

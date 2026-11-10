
import os
from pathlib import Path

from dotenv import dotenv_values
from supabase import Client, create_client


RAIZ_PROJETO = Path(__file__).resolve().parents[2]
ARQUIVO_ENV = RAIZ_PROJETO / ".env"


def criar_cliente_supabase() -> Client:
    configuracoes = {}

    # Carrega o .env quando ele existir.
    if ARQUIVO_ENV.is_file():
        configuracoes = dotenv_values(ARQUIVO_ENV)

    # Prioriza variáveis de ambiente.
    url = os.getenv("SUPABASE_URL") or configuracoes.get(
        "SUPABASE_URL"
    )

    chave = os.getenv("SUPABASE_KEY") or configuracoes.get(
        "SUPABASE_KEY"
    )

    print("URL do Supabase configurada:", bool(url))
    print("Chave do Supabase configurada:", bool(chave))

    if not url or not chave:
        raise RuntimeError(
            "As configurações do Supabase não foram encontradas."
        )

    cliente = create_client(url, chave)

    return cliente

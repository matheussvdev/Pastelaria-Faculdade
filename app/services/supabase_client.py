
import os
from pathlib import Path

from dotenv import dotenv_values
from supabase import Client, create_client


RAIZ_PROJETO = Path(__file__).resolve().parents[2]
ARQUIVO_ENV = RAIZ_PROJETO / ".env"


def carregar_configuracoes() -> tuple[str, str]:
    """
    Carrega as configurações públicas do Supabase.

    Prioridade:
    1. Variáveis de ambiente
    2. Arquivo .env
    3. Configuração pública do aplicativo
    """

    configuracoes = {}

    if ARQUIVO_ENV.is_file():
        configuracoes = dotenv_values(ARQUIVO_ENV)

    url = os.getenv("SUPABASE_URL") or configuracoes.get(
        "SUPABASE_URL"
    )

    chave = os.getenv("SUPABASE_KEY") or configuracoes.get(
        "SUPABASE_KEY"
    )

    if not url or not chave:
        from app.supabase_public_config import (
            SUPABASE_URL,
            SUPABASE_KEY,
        )

        url = url or SUPABASE_URL
        chave = chave or SUPABASE_KEY

    if not url or not chave:
        raise RuntimeError(
            "Configurações do Supabase não encontradas."
        )

    return url, chave


def criar_cliente_supabase() -> Client:
    """
    Inicializa o cliente Supabase utilizando
    configurações previamente validadas.
    """

    url, chave = carregar_configuracoes()

    try:
        cliente = create_client(url, chave)

    except Exception as erro:
        raise RuntimeError(
            "Não foi possível inicializar o cliente Supabase."
        ) from erro

    return cliente


from pathlib import Path

from dotenv import dotenv_values
from supabase import Client, create_client


RAIZ_PROJETO = Path(__file__).resolve().parents[2]
ARQUIVO_ENV = RAIZ_PROJETO / ".env"


def criar_cliente_supabase() -> Client:
    configuracoes = dotenv_values(ARQUIVO_ENV)

    url = configuracoes.get("SUPABASE_URL")
    chave = configuracoes.get("SUPABASE_KEY")

    print("Arquivo encontrado:", ARQUIVO_ENV.is_file())
    print("URL encontrada:", bool(url))
    print("Chave encontrada:", bool(chave))

    if not url or not chave:
        raise RuntimeError(
            "As credenciais do Supabase não foram encontradas."
        )

    cliente = create_client(url, chave)

    return cliente

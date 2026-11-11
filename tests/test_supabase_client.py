
from unittest.mock import MagicMock, patch

import pytest

from app.services import supabase_client


def test_carregar_configuracoes_variaveis_ambiente(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://teste.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "chave_teste")

    url, chave = supabase_client.carregar_configuracoes()

    assert url == "https://teste.supabase.co"
    assert chave == "chave_teste"


def test_carregar_configuracoes_arquivo_env(monkeypatch, tmp_path):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)

    arquivo_env = tmp_path / ".env"

    arquivo_env.write_text(
        "SUPABASE_URL=https://arquivo.supabase.co\n"
        "SUPABASE_KEY=chave_arquivo\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        supabase_client,
        "ARQUIVO_ENV",
        arquivo_env,
    )

    url, chave = supabase_client.carregar_configuracoes()

    assert url == "https://arquivo.supabase.co"
    assert chave == "chave_arquivo"


def test_criar_cliente_supabase_sucesso():
    cliente_simulado = MagicMock()

    with patch.object(
        supabase_client,
        "carregar_configuracoes",
        return_value=("https://teste.supabase.co", "chave_teste"),
    ):
        with patch.object(
            supabase_client,
            "create_client",
            return_value=cliente_simulado,
        ) as criar_cliente:
            resultado = supabase_client.criar_cliente_supabase()

    assert resultado is cliente_simulado

    criar_cliente.assert_called_once_with(
        "https://teste.supabase.co",
        "chave_teste",
    )


def test_criar_cliente_supabase_erro():
    with patch.object(
        supabase_client,
        "carregar_configuracoes",
        return_value=("https://teste.supabase.co", "chave_teste"),
    ):
        with patch.object(
            supabase_client,
            "create_client",
            side_effect=Exception("Falha simulada"),
        ):
            with pytest.raises(
                RuntimeError,
                match="Não foi possível inicializar",
            ):
                supabase_client.criar_cliente_supabase()

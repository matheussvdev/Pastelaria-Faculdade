
import pytest
from unittest.mock import MagicMock

from app.services.comandas_service import (
    criar_comanda_bd,
    fechar_comanda_bd,
)


def test_criar_comanda_sem_nome():
    cliente = MagicMock()

    with pytest.raises(ValueError, match="Informe o nome"):
        criar_comanda_bd(
            cliente,
            "   ",
            [{"produto_id": 1, "quantidade": 2}],
        )

    cliente.rpc.assert_not_called()


def test_criar_comanda_sem_produtos():
    cliente = MagicMock()

    with pytest.raises(ValueError, match="Selecione pelo menos"):
        criar_comanda_bd(
            cliente,
            "João",
            [],
        )

    cliente.rpc.assert_not_called()


def test_criar_comanda_quantidade_invalida():
    cliente = MagicMock()

    with pytest.raises(ValueError, match="quantidade"):
        criar_comanda_bd(
            cliente,
            "Maria",
            [{"produto_id": 1, "quantidade": 0}],
        )

    cliente.rpc.assert_not_called()


def test_fechar_comanda_id_invalido():
    cliente = MagicMock()

    with pytest.raises(ValueError, match="ID da comanda inválido"):
        fechar_comanda_bd(cliente, -1)

    cliente.rpc.assert_not_called()


def test_fechar_comanda_sem_confirmacao():
    cliente = MagicMock()
    cliente.rpc.return_value.execute.return_value.data = None

    with pytest.raises(RuntimeError, match="não confirmou"):
        fechar_comanda_bd(cliente, 10)

    cliente.rpc.assert_called_once_with(
        "fechar_comanda",
        {"p_comanda_id": 10},
    )

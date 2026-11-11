
from decimal import Decimal
from unittest.mock import MagicMock

from app.services.comandas_service import (
    criar_comanda_bd,
    listar_comandas_abertas_bd,
    buscar_detalhes_comanda_bd,
    fechar_comanda_bd,
)


def test_integracao_criar_comanda():
    cliente = MagicMock()
    cliente.rpc.return_value.execute.return_value.data = 15

    resultado = criar_comanda_bd(
        cliente,
        "  João  ",
        [{"produto_id": 2, "quantidade": 3}],
    )

    assert resultado == 15

    cliente.rpc.assert_called_once_with(
        "criar_comanda",
        {
            "p_cliente": "João",
            "p_itens": [
                {"produto_id": 2, "quantidade": 3}
            ],
        },
    )


def test_integracao_listar_comandas_abertas():
    cliente = MagicMock()

    comandas = [
        {"id": 1, "cliente": "Maria", "status": "aberta"},
        {"id": 2, "cliente": "Pedro", "status": "aberta"},
    ]

    cliente.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = comandas

    resultado = listar_comandas_abertas_bd(cliente)

    assert len(resultado) == 2
    assert resultado[0]["cliente"] == "Maria"

    cliente.table.assert_called_once_with("comandas")


def test_integracao_calcular_total_comanda():
    cliente = MagicMock()

    cliente.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value.data = {
        "id": 10,
        "cliente": "Ana",
        "status": "aberta",
    }

    itens = [
        {
            "id": 1,
            "produto_id": 2,
            "quantidade": 2,
            "preco_unitario": "17.00",
            "produtos": {"nome": "Pizza"},
        },
        {
            "id": 2,
            "produto_id": 3,
            "quantidade": 1,
            "preco_unitario": "8.50",
            "produtos": {"nome": "Bebida"},
        },
    ]

    cliente.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = itens

    resultado = buscar_detalhes_comanda_bd(cliente, 10)

    assert resultado["total"] == Decimal("42.50")
    assert len(resultado["itens"]) == 2
    assert resultado["itens"][0]["subtotal"] == Decimal("34.00")


def test_integracao_fechar_comanda():
    cliente = MagicMock()
    cliente.rpc.return_value.execute.return_value.data = "42.50"

    resultado = fechar_comanda_bd(cliente, 10)

    assert resultado == Decimal("42.50")

    cliente.rpc.assert_called_once_with(
        "fechar_comanda",
        {"p_comanda_id": 10},
    )


from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

COMANDAS = [
    {
        "id": 1,
        "cliente": "Carlos",
        "horario": "15:42",
        "status": "aberta",
        "produtos": [
            {"nome": "Pastel de Carne", "quantidade": 2, "preco": 8.50},
            {"nome": "Pastel de Queijo", "quantidade": 1, "preco": 8.00},
        ],
    },
    {
        "id": 2,
        "cliente": "Fernanda",
        "horario": "16:10",
        "status": "aberta",
        "produtos": [
            {"nome": "Pastel de Frango", "quantidade": 2, "preco": 8.00},
        ],
    },
]


CARDAPIO = [
    {"nome": "Pastel de Carne", "preco": 8.50},
    {"nome": "Pastel de Queijo", "preco": 8.00},
    {"nome": "Pastel de Frango", "preco": 8.00},
    {"nome": "Pastel de Pizza", "preco": 8.50},
    {"nome": "Pastel de Palmito", "preco": 9.00},
    {"nome": "Refrigerante", "preco": 6.00},
    {"nome": "Água Mineral", "preco": 3.50},
]


def calcular_total(comanda):
    total = sum(
        Decimal(str(item["preco"])) * item["quantidade"]
        for item in comanda["produtos"]
    )
    return float(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def formatar_moeda(valor):
    return f"R$ {valor:.2f}".replace(".", ",")


def criar_comanda(nome, produtos):
    nome = " ".join(nome.split())

    if not nome:
        raise ValueError("Informe o nome do cliente.")

    if not produtos:
        raise ValueError("Selecione pelo menos um produto.")

    nova = {
        "id": max((c["id"] for c in COMANDAS), default=0) + 1,
        "cliente": nome,
        "horario": datetime.now().strftime("%H:%M"),
        "status": "aberta",
        "produtos": [dict(item) for item in produtos],
    }

    COMANDAS.append(nova)
    return nova


def adicionar_produtos(comanda, produtos):
    if comanda["status"] != "aberta":
        raise ValueError("Não é possível alterar uma comanda fechada.")

    for novo in produtos:
        existente = next(
            (p for p in comanda["produtos"] if p["nome"] == novo["nome"]),
            None,
        )
        if existente:
            existente["quantidade"] += novo["quantidade"]
        else:
            comanda["produtos"].append(dict(novo))



def fechar_comanda(comanda):
    if comanda["status"] != "aberta":
        raise ValueError("Esta comanda já está fechada.")

    comanda["status"] = "fechada"
    comanda["fechada_em"] = datetime.now().isoformat(
        timespec="seconds"
    )

    return comanda


def criar_comanda_bd(cliente_supabase, nome_cliente, itens):
    nome_cliente = nome_cliente.strip()

    if not nome_cliente:
        raise ValueError("Informe o nome do cliente.")

    if not itens:
        raise ValueError("Selecione pelo menos um produto.")

    itens_para_banco = []

    for item in itens:
        quantidade = int(item["quantidade"])

        if quantidade <= 0:
            raise ValueError(
                "A quantidade deve ser maior que zero."
            )

        itens_para_banco.append({
            "produto_id": int(item["produto_id"]),
            "quantidade": quantidade,
        })

    resposta = cliente_supabase.rpc(
        "criar_comanda",
        {
            "p_cliente": nome_cliente,
            "p_itens": itens_para_banco,
        },
    ).execute()

    if resposta.data is None:
        raise RuntimeError(
            "O banco não retornou o ID da comanda."
        )

    return int(resposta.data)

    
from decimal import Decimal


def listar_comandas_abertas_bd(cliente_supabase):
    resposta = (
        cliente_supabase.table("comandas")
        .select("id, cliente, status, aberta_em")
        .eq("status", "aberta")
        .order("aberta_em", desc=True)
        .execute()
    )

    return resposta.data or []


def listar_comandas_abertas_com_detalhes_bd(cliente_supabase):
    """
    Busca todas as comandas abertas e seus itens em lote,
    evitando consultas individuais para cada comanda.
    """

    resposta_comandas = (
        cliente_supabase.table("comandas")
        .select("id, cliente, status, aberta_em, fechada_em")
        .eq("status", "aberta")
        .order("aberta_em", desc=True)
        .execute()
    )

    registros = resposta_comandas.data or []

    if not registros:
        return []

    ids_comandas = [
        registro["id"]
        for registro in registros
    ]

    resposta_itens = (
        cliente_supabase.table("itens_comanda")
        .select(
            "id, comanda_id, produto_id, quantidade, "
            "preco_unitario, produtos(nome)"
        )
        .in_("comanda_id", ids_comandas)
        .order("id")
        .execute()
    )

    comandas_por_id = {}

    for registro in registros:
        comandas_por_id[registro["id"]] = {
            **registro,
            "itens": [],
            "total": Decimal("0.00"),
        }

    for item in resposta_itens.data or []:
        comanda = comandas_por_id.get(
            item["comanda_id"]
        )

        if comanda is None:
            continue

        quantidade = int(item["quantidade"])
        preco = Decimal(str(item["preco_unitario"]))
        subtotal = preco * quantidade

        produto = item.get("produtos") or {}

        comanda["itens"].append({
            "id": item["id"],
            "produto_id": item["produto_id"],
            "nome": produto.get("nome", "Produto"),
            "quantidade": quantidade,
            "preco_unitario": preco,
            "subtotal": subtotal,
        })

        comanda["total"] += subtotal

    return list(comandas_por_id.values())



def buscar_detalhes_comanda_bd(cliente_supabase, comanda_id):
    resposta_comanda = (
        cliente_supabase.table("comandas")
        .select("id, cliente, status, aberta_em, fechada_em")
        .eq("id", comanda_id)
        .single()
        .execute()
    )

    comanda = resposta_comanda.data

    resposta_itens = (
        cliente_supabase.table("itens_comanda")
        .select(
            "id, produto_id, quantidade, preco_unitario, "
            "produtos(nome)"
        )
        .eq("comanda_id", comanda_id)
        .order("id")
        .execute()
    )

    itens = []
    total = Decimal("0.00")

    for item in resposta_itens.data or []:
        quantidade = int(item["quantidade"])
        preco = Decimal(str(item["preco_unitario"]))
        subtotal = preco * quantidade
        total += subtotal

        produto = item.get("produtos") or {}

        itens.append({
            "id": item["id"],
            "produto_id": item["produto_id"],
            "nome": produto.get("nome", "Produto"),
            "quantidade": quantidade,
            "preco_unitario": preco,
            "subtotal": subtotal,
        })

    return {
        **comanda,
        "itens": itens,
        "total": total,
    }


def fechar_comanda_bd(cliente_supabase, comanda_id):
    if not isinstance(comanda_id, int) or comanda_id <= 0:
        raise ValueError("ID da comanda inválido.")

    resposta = cliente_supabase.rpc(
        "fechar_comanda",
        {
            "p_comanda_id": comanda_id,
        },
    ).execute()

    if resposta.data is None:
        raise RuntimeError(
            "O banco não confirmou o fechamento."
        )

    return Decimal(str(resposta.data))


def adicionar_itens_comanda_bd(
    cliente_supabase,
    comanda_id,
    itens,
):
    if not itens:
        raise ValueError(
            "Selecione pelo menos um produto."
        )

    itens_para_banco = []

    for item in itens:
        quantidade = int(item["quantidade"])

        if quantidade <= 0:
            raise ValueError(
                "A quantidade deve ser maior que zero."
            )

        itens_para_banco.append({
            "produto_id": int(item["produto_id"]),
            "quantidade": quantidade,
        })

    cliente_supabase.rpc(
        "adicionar_itens_comanda",
        {
            "p_comanda_id": int(comanda_id),
            "p_itens": itens_para_banco,
        },
    ).execute()

def listar_comandas_fechadas_bd(cliente_supabase):
    resposta = (
        cliente_supabase.table("comandas")
        .select("id, cliente, status, aberta_em, fechada_em")
        .eq("status", "fechada")
        .order("fechada_em", desc=True)
        .execute()
    )

    return resposta.data or []
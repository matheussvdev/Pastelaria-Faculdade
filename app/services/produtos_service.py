
from decimal import Decimal


def listar_produtos(cliente_supabase):
    resposta = (
        cliente_supabase.table("produtos")
        .select("id, nome, categoria, preco, disponivel")
        .eq("disponivel", True)
        .order("nome")
        .execute()
    )

    produtos = []

    for produto in resposta.data or []:
        produtos.append({
            "id": produto["id"],
            "nome": produto["nome"],
            "categoria": produto["categoria"],
            "preco": Decimal(str(produto["preco"])),
            "disponivel": produto["disponivel"],
        })

    return produtos

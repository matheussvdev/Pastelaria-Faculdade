
from decimal import Decimal, InvalidOperation


CATEGORIAS_VALIDAS = {"pastel", "bebida", "extra"}


def validar_produto(nome, categoria, preco):
    nome = (nome or "").strip()
    categoria = (categoria or "").strip().lower()

    if not nome:
        raise ValueError("Informe o nome do produto.")

    if categoria not in CATEGORIAS_VALIDAS:
        raise ValueError("Categoria inválida.")

    try:
        valor = Decimal(str(preco))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Informe um preço válido.")

    if not valor.is_finite() or valor <= 0:
        raise ValueError("O preço deve ser maior que zero.")

    if valor.as_tuple().exponent < -2:
        raise ValueError("Use no máximo duas casas decimais.")

    if valor > Decimal("99999999.99"):
        raise ValueError("Preço acima do limite permitido.")

    return nome, categoria, valor


def listar_todos_produtos_bd(cliente_supabase):
    resposta = (
        cliente_supabase.table("produtos")
        .select("id, nome, categoria, preco, disponivel")
        .order("nome")
        .execute()
    )

    return resposta.data or []


def cadastrar_produto_bd(
    cliente_supabase,
    nome,
    categoria,
    preco,
):
    nome, categoria, valor = validar_produto(
        nome,
        categoria,
        preco,
    )

    resposta = (
        cliente_supabase.table("produtos")
        .insert({
            "nome": nome,
            "categoria": categoria,
            "preco": str(valor),
            "disponivel": True,
        })
        .execute()
    )

    return resposta.data


def atualizar_produto_bd(
    cliente_supabase,
    produto_id,
    nome,
    categoria,
    preco,
):
    nome, categoria, valor = validar_produto(
        nome,
        categoria,
        preco,
    )

    resposta = (
        cliente_supabase.table("produtos")
        .update({
            "nome": nome,
            "categoria": categoria,
            "preco": str(valor),
        })
        .eq("id", int(produto_id))
        .execute()
    )

    return resposta.data


def alterar_disponibilidade_bd(
    cliente_supabase,
    produto_id,
    disponivel,
):
    if not isinstance(disponivel, bool):
        raise ValueError("Disponibilidade inválida.")

    resposta = (
        cliente_supabase.table("produtos")
        .update({
            "disponivel": disponivel,
        })
        .eq("id", int(produto_id))
        .execute()
    )

    return resposta.data

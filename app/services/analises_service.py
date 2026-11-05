
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo
from datetime import date, datetime, time, timedelta, timezone


FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")


def calcular_periodo(filtro="30_dias"):
    agora = datetime.now(FUSO_BRASIL)
    hoje = agora.date()

    if filtro == "hoje":
        inicio = hoje
        fim = hoje + timedelta(days=1)

    elif filtro == "7_dias":
        inicio = hoje - timedelta(days=6)
        fim = hoje + timedelta(days=1)

    elif filtro == "30_dias":
        inicio = hoje - timedelta(days=29)
        fim = hoje + timedelta(days=1)

    elif filtro == "mes":
        inicio = hoje.replace(day=1)

        if hoje.month == 12:
            fim = hoje.replace(
                year=hoje.year + 1,
                month=1,
                day=1,
            )
        else:
            fim = hoje.replace(
                month=hoje.month + 1,
                day=1,
            )

    else:
        raise ValueError("Filtro de período inválido.")

    inicio_data = datetime.combine(
        inicio,
        datetime.min.time(),
        tzinfo=FUSO_BRASIL,
    )

    fim_data = datetime.combine(
        fim,
        datetime.min.time(),
        tzinfo=FUSO_BRASIL,
    )

    return (
        inicio_data.astimezone(timezone.utc).isoformat(),
        fim_data.astimezone(timezone.utc).isoformat(),
    )


def buscar_resumo_vendas_bd(
    cliente_supabase,
    filtro="30_dias",
):
    inicio, fim = calcular_periodo(filtro)

    resposta = cliente_supabase.rpc(
        "resumo_vendas",
        {
            "p_inicio": inicio,
            "p_fim": fim,
        },
    ).execute()

    if not isinstance(resposta.data, dict):
        raise RuntimeError(
            "O Supabase retornou um resumo inválido."
        )

    dados = resposta.data

    ranking = []

    for produto in dados.get("ranking") or []:
        ranking.append({
            "produto_id": produto["produto_id"],
            "nome": produto["nome"],
            "quantidade": int(produto["quantidade"]),
            "faturamento": Decimal(
                str(produto["faturamento"])
            ),
        })

    return {
        "total_vendas": int(dados["total_vendas"]),
        "faturamento": Decimal(
            str(dados["faturamento"])
        ),
        "itens_vendidos": int(dados["itens_vendidos"]),
        "ticket_medio": Decimal(
            str(dados["ticket_medio"])
        ),
        "ranking": ranking,
    }


def buscar_faturamento_diario_bd(
    cliente_supabase,
    filtro="30_dias",
):
    inicio, fim = calcular_periodo(filtro)

    resposta = cliente_supabase.rpc(
        "faturamento_diario",
        {
            "p_inicio": inicio,
            "p_fim": fim,
        },
    ).execute()

    resultado = []

    for registro in resposta.data or []:
        resultado.append({
            "dia": registro["dia"],
            "faturamento": Decimal(
                str(registro["faturamento"])
            ),
            "total_vendas": int(
                registro["total_vendas"]
            ),
        })

    return resultado

    
def calcular_periodo_personalizado(data_inicio, data_fim):
    """
    Recebe duas datas no formato YYYY-MM-DD
    ou objetos date.

    Retorna o início inclusivo e o fim exclusivo
    em UTC, para consulta no Supabase.
    """

    if isinstance(data_inicio, str):
        data_inicio = date.fromisoformat(data_inicio)

    if isinstance(data_fim, str):
        data_fim = date.fromisoformat(data_fim)

    if not isinstance(data_inicio, date) or isinstance(data_inicio, datetime):
        raise ValueError("Data inicial inválida.")

    if not isinstance(data_fim, date) or isinstance(data_fim, datetime):
        raise ValueError("Data final inválida.")

    if data_inicio > data_fim:
        raise ValueError(
            "A data inicial não pode ser posterior à data final."
        )

    fuso = ZoneInfo("America/Sao_Paulo")

    inicio_local = datetime.combine(
        data_inicio,
        time.min,
        tzinfo=fuso,
    )

    fim_local = datetime.combine(
        data_fim + timedelta(days=1),
        time.min,
        tzinfo=fuso,
    )

    inicio_utc = inicio_local.astimezone(timezone.utc)
    fim_utc = fim_local.astimezone(timezone.utc)

    return inicio_utc.isoformat(), fim_utc.isoformat()


def buscar_resumo_personalizado_bd(
    cliente_supabase,
    data_inicio,
    data_fim,
):
    inicio, fim = calcular_periodo_personalizado(
        data_inicio,
        data_fim,
    )

    resposta = cliente_supabase.rpc(
        "resumo_vendas",
        {
            "p_inicio": inicio,
            "p_fim": fim,
        },
    ).execute()

    if resposta.data is None:
        raise ValueError(
            "Não foi possível consultar o resumo de vendas."
        )

    return resposta.data


def buscar_faturamento_personalizado_bd(
    cliente_supabase,
    data_inicio,
    data_fim,
):
    inicio, fim = calcular_periodo_personalizado(
        data_inicio,
        data_fim,
    )

    resposta = cliente_supabase.rpc(
        "faturamento_diario",
        {
            "p_inicio": inicio,
            "p_fim": fim,
        },
    ).execute()

    return resposta.data or []


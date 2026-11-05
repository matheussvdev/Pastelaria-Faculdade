
import flet as ft
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_CEILING
from zoneinfo import ZoneInfo

from app.theme.colors import AppColors as C
from app.services.analises_service import (
    buscar_resumo_vendas_bd,
    buscar_faturamento_diario_bd,
    buscar_resumo_personalizado_bd,
    buscar_faturamento_personalizado_bd,
)


def formatar_moeda(valor):
    numero = Decimal(str(valor))
    return f"R$ {numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def analises_vendas_screen(page, voltar, cliente_supabase):
    filtro_atual = "30_dias"
    periodo_personalizado = None

    indicadores = ft.Column(spacing=12)
    lista_ranking = ft.Column(spacing=10)
    grafico_diario = ft.Column(spacing=10)

    status = ft.Text("", size=12, color=C.TEXT_SECONDARY)

    # =========================================
    # MENSAGENS DE ERRO
    # =========================================

    def mostrar_erro(texto):
        page.show_dialog(
            ft.SnackBar(content=ft.Text(texto))
        )

    # =========================================
    # INDICADORES FINANCEIROS
    # =========================================

    def criar_indicador(titulo, valor, icone):
        return ft.Container(
            bgcolor=C.SURFACE,
            border_radius=14,
            border=ft.Border.all(1, C.BORDER),
            padding=14,
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Icon(
                        icone,
                        color=C.PRIMARY,
                        size=25,
                    ),
                    ft.Text(
                        titulo,
                        size=12,
                        color=C.TEXT_SECONDARY,
                    ),
                    ft.Text(
                        str(valor),
                        size=19,
                        weight=ft.FontWeight.BOLD,
                        color=C.TEXT,
                    ),
                ],
                spacing=8,
            ),
        )

    # =========================================
    # RANKING DE PRODUTOS
    # =========================================

    def criar_linha_ranking(produto, posicao, maior):
        quantidade = produto["quantidade"]
        proporcao = quantidade / maior if maior > 0 else 0

        return ft.Container(
            bgcolor=C.SURFACE,
            border_radius=12,
            padding=14,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"{posicao}º",
                                size=17,
                                weight=ft.FontWeight.BOLD,
                                color=C.PRIMARY,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        produto["nome"],
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=C.TEXT,
                                    ),
                                    ft.Text(
                                        f"{quantidade} unidades vendidas",
                                        size=12,
                                        color=C.TEXT_SECONDARY,
                                    ),
                                ],
                                expand=True,
                                spacing=4,
                            ),
                            ft.Text(
                                formatar_moeda(
                                    produto["faturamento"]
                                ),
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=C.PRIMARY,
                            ),
                        ],
                    ),
                    ft.ProgressBar(
                        value=proporcao,
                        color=C.PRIMARY,
                        bgcolor=C.BORDER,
                        height=7,
                        border_radius=5,
                    ),
                ],
                spacing=12,
            ),
        )

    # =========================================
    # FILTROS DE DATA
    # =========================================

    def datas_do_filtro(filtro):
        hoje = datetime.now(
            ZoneInfo("America/Sao_Paulo")
        ).date()

        if filtro == "hoje":
            return hoje, hoje

        if filtro == "7_dias":
            return hoje - timedelta(days=6), hoje

        if filtro == "30_dias":
            return hoje - timedelta(days=29), hoje

        if filtro == "mes":
            return hoje.replace(day=1), hoje

        raise ValueError("Filtro inválido.")

    # =========================================
    # GRÁFICO FINANCEIRO
    # =========================================

    def preencher_grafico_diario(registros, filtro, periodo=None):
        grafico_diario.controls.clear()

        if periodo is not None:
            inicio, fim = periodo
        else:
            inicio, fim = datas_do_filtro(filtro)

        valores = {
            date.fromisoformat(item["dia"]): item
            for item in registros
        }

        dias = []
        atual = inicio

        while atual <= fim:
            registro = valores.get(atual, {})

            dias.append({
                "dia": atual,
                "faturamento": Decimal(
                    str(registro.get("faturamento", 0))
                ),
                "total_vendas": int(
                    registro.get("total_vendas", 0)
                ),
            })

            atual += timedelta(days=1)

        # Dias mais recentes primeiro
        dias.reverse()

        maior = max(
            (item["faturamento"] for item in dias),
            default=Decimal("0"),
        )

        # Escala do eixo Y
        if maior > 0:
            intervalo = (
                maior / Decimal("4")
            ).quantize(
                Decimal("1"),
                rounding=ROUND_CEILING,
            )
            intervalo = max(intervalo, Decimal("1"))
        else:
            intervalo = Decimal("10")

        limite = intervalo * 4

        altura_grafico = 200
        largura_coluna = 70
        espacamento = 8

        # =====================================
        # EIXO Y FIXO
        # =====================================

        marcadores = []

        for nivel in range(4, -1, -1):
            marcadores.append(
                ft.Container(
                    height=50,
                    alignment=ft.Alignment.TOP_RIGHT,
                    content=ft.Text(
                        formatar_moeda(intervalo * nivel),
                        size=10,
                        color=C.TEXT_SECONDARY,
                    ),
                )
            )

        eixo_y = ft.Container(
            width=82,
            content=ft.Column(
                controls=marcadores,
                spacing=0,
            ),
        )

        # =====================================
        # COLUNAS VERTICAIS
        # =====================================

        colunas = []

        for item in dias:
            valor = item["faturamento"]

            proporcao = (
                float(valor / limite)
                if limite > 0
                else 0
            )

            altura = max(
                0,
                min(
                    altura_grafico,
                    proporcao * altura_grafico,
                ),
            )

            barra = ft.Container(
                width=34,
                height=max(1, altura),
                bgcolor=(
                    C.PRIMARY if valor > 0 else C.BORDER
                ),
                border_radius=ft.BorderRadius.only(
                    top_left=5,
                    top_right=5,
                ),
            )

            area_coluna = ft.Container(
                width=largura_coluna,
                height=altura_grafico,
                alignment=ft.Alignment.BOTTOM_CENTER,
                content=barra,
            )

            colunas.append(
                ft.Container(
                    width=largura_coluna,
                    content=ft.Column(
                        controls=[
                            area_coluna,
                            ft.Text(
                                item["dia"].strftime("%d/%m"),
                                size=11,
                                color=C.TEXT,
                                width=largura_coluna,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                f'{item["total_vendas"]} vendas',
                                size=10,
                                color=C.TEXT_SECONDARY,
                                width=largura_coluna,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        spacing=8,
                        horizontal_alignment=(
                            ft.CrossAxisAlignment.CENTER
                        ),
                    ),
                )
            )

        # =====================================
        # LINHAS HORIZONTAIS DE REFERÊNCIA
        # =====================================

        largura_total = max(
            1,
            len(dias) * (largura_coluna + espacamento),
        )

        linhas = [
            ft.Container(
                height=50,
                border=ft.Border(
                    top=ft.BorderSide(1, C.BORDER)
                ),
            )
            for _ in range(4)
        ]

        linhas.append(
            ft.Container(
                height=1,
                bgcolor=C.BORDER,
            )
        )

        grade = ft.Container(
            width=largura_total,
            height=altura_grafico,
            content=ft.Column(
                controls=linhas,
                spacing=0,
            ),
        )

        area_grafico = ft.Stack(
            controls=[
                grade,
                ft.Row(
                    controls=colunas,
                    spacing=espacamento,
                    vertical_alignment=(
                        ft.CrossAxisAlignment.START
                    ),
                ),
            ],
            width=largura_total,
            height=altura_grafico + 55,
        )

        # =====================================
        # GRÁFICO COMPLETO
        # =====================================

        grafico_diario.controls.append(
            ft.Container(
                bgcolor=C.SURFACE,
                border_radius=14,
                padding=16,
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Faturamento por dia",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color=C.TEXT,
                        ),
                        ft.Text(
                            "Dias mais recentes primeiro",
                            size=11,
                            color=C.TEXT_SECONDARY,
                        ),
                        ft.Row(
                            controls=[
                                eixo_y,
                                ft.Row(
                                    controls=[area_grafico],
                                    scroll=ft.ScrollMode.AUTO,
                                    expand=True,
                                ),
                            ],
                            spacing=8,
                            vertical_alignment=(
                                ft.CrossAxisAlignment.START
                            ),
                        ),
                        ft.Text(
                            "Deslize horizontalmente para consultar outros dias",
                            size=10,
                            color=C.TEXT_SECONDARY,
                        ),
                    ],
                    spacing=12,
                ),
            )
        )

    # =========================================
    # ATUALIZAR DASHBOARD
    # =========================================

    def atualizar_dashboard(filtro, periodo=None):
        nonlocal filtro_atual, periodo_personalizado

        status.value = "Carregando análises..."
        page.update()

        try:
            if filtro == "personalizado":
                if periodo is None:
                    raise ValueError(
                        "Selecione as datas do período."
                    )

                inicio, fim = periodo

                dados = buscar_resumo_personalizado_bd(
                    cliente_supabase,
                    inicio,
                    fim,
                )

                vendas_diarias = buscar_faturamento_personalizado_bd(
                    cliente_supabase,
                    inicio,
                    fim,
                )

            else:
                dados = buscar_resumo_vendas_bd(
                    cliente_supabase,
                    filtro,
                )

                vendas_diarias = buscar_faturamento_diario_bd(
                    cliente_supabase,
                    filtro,
                )

            preencher_grafico_diario(
                vendas_diarias,
                filtro,
                periodo,
            )

            filtro_atual = filtro
            periodo_personalizado = (
                periodo if filtro == "personalizado" else None
            )

            # Atualizar indicadores
            indicadores.controls.clear()

            indicadores.controls.extend([
                ft.Row(
                    controls=[
                        criar_indicador(
                            "Faturamento",
                            formatar_moeda(
                                dados["faturamento"]
                            ),
                            ft.Icons.ATTACH_MONEY,
                        ),
                        criar_indicador(
                            "Vendas",
                            dados["total_vendas"],
                            ft.Icons.RECEIPT_LONG,
                        ),
                    ],
                    spacing=12,
                ),
                ft.Row(
                    controls=[
                        criar_indicador(
                            "Ticket médio",
                            formatar_moeda(
                                dados["ticket_medio"]
                            ),
                            ft.Icons.TRENDING_UP,
                        ),
                        criar_indicador(
                            "Itens vendidos",
                            dados["itens_vendidos"],
                            ft.Icons.SHOPPING_BAG_OUTLINED,
                        ),
                    ],
                    spacing=12,
                ),
            ])

            # Atualizar ranking
            lista_ranking.controls.clear()
            ranking = dados["ranking"]

            if ranking:
                maior_quantidade = max(
                    produto["quantidade"]
                    for produto in ranking
                )

                for posicao, produto in enumerate(
                    ranking,
                    start=1,
                ):
                    lista_ranking.controls.append(
                        criar_linha_ranking(
                            produto,
                            posicao,
                            maior_quantidade,
                        )
                    )
            else:
                lista_ranking.controls.append(
                    ft.Container(
                        padding=24,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text(
                            "Nenhuma venda encontrada neste período.",
                            color=C.TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    )
                )

            status.value = "Dados de comandas fechadas"

        except Exception as erro:
            print(f"Erro ao carregar análises: {erro}")

            indicadores.controls.clear()
            grafico_diario.controls.clear()
            lista_ranking.controls.clear()

            status.value = "Erro ao carregar os dados."

            mostrar_erro(
                "Não foi possível consultar as análises. "
                "Verifique o terminal."
            )

        page.update()

    # =========================================
    # CAMPOS DE DATA PERSONALIZADA
    # =========================================

    hoje = datetime.now(
        ZoneInfo("America/Sao_Paulo")
    ).date()

    data_inicial = ft.TextField(
        label="Data inicial (DD/MM/AAAA)",
        value=(hoje - timedelta(days=6)).strftime("%d/%m/%Y"),
        expand=True,
    )

    data_final = ft.TextField(
        label="Data final (DD/MM/AAAA)",
        value=hoje.strftime("%d/%m/%Y"),
        expand=True,
    )

    def converter_data(texto):
        return datetime.strptime(
            (texto or "").strip(),
            "%d/%m/%Y",
        ).date()

    # =========================================
    # APLICAR FILTRO PERSONALIZADO
    # =========================================

    def aplicar_periodo(e):
        try:
            inicio = converter_data(data_inicial.value)
            fim = converter_data(data_final.value)

            if inicio > fim:
                raise ValueError(
                    "A data inicial não pode ser posterior à final."
                )

            if (fim - inicio).days > 366:
                raise ValueError(
                    "Selecione um período de até 367 dias."
                )

        except ValueError as erro:
            status.value = (
                str(erro)
                if (
                    "posterior" in str(erro)
                    or "367" in str(erro)
                )
                else "Informe datas válidas no formato DD/MM/AAAA."
            )
            page.update()
            return

        atualizar_dashboard(
            "personalizado",
            (inicio, fim),
        )

    # =========================================
    # PAINEL DO FILTRO PERSONALIZADO
    # =========================================

    campos_personalizados = ft.Container(
        visible=False,
        bgcolor=C.SURFACE,
        border_radius=12,
        padding=14,
        content=ft.Column(
            controls=[
                ft.Text(
                    "Escolha o período",
                    color=C.TEXT,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row(
                    controls=[
                        data_inicial,
                        data_final,
                    ],
                    spacing=10,
                ),
                ft.Button(
    content="Aplicar filtro",
    on_click=aplicar_periodo,
),
            ],
            spacing=10,
        ),
    )

    # =========================================
    # SELEÇÃO DO PERÍODO
    # =========================================

    def selecionar_periodo(filtro):
        campos_personalizados.visible = (
            filtro == "personalizado"
        )

        if filtro == "personalizado":
            status.value = (
                "Informe as datas e clique em Aplicar filtro."
            )
            page.update()
            return

        atualizar_dashboard(filtro)

    # =========================================
    # BOTÃO DE ATUALIZAR
    # =========================================

    def atualizar_ao_clicar():
        if filtro_atual == "personalizado":
            atualizar_dashboard(
                filtro_atual,
                periodo_personalizado,
            )
        else:
            atualizar_dashboard(filtro_atual)

    # =========================================
    # FILTROS
    # =========================================

    filtros = ft.Dropdown(
        label="Período",
        value="30_dias",
        options=[
            ft.dropdown.Option("hoje", "Hoje"),
            ft.dropdown.Option("7_dias", "Últimos 7 dias"),
            ft.dropdown.Option("30_dias", "Últimos 30 dias"),
            ft.dropdown.Option("mes", "Este mês"),
            ft.dropdown.Option(
                "personalizado",
                "Personalizado",
            ),
        ],
        on_select=lambda e: selecionar_periodo(
            e.control.value
        ),
    )

    # =========================================
    # CABEÇALHO
    # =========================================

    cabecalho = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=C.TEXT,
                on_click=lambda e: voltar(),
            ),
            ft.Text(
                "Análises de Vendas",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=C.TEXT,
                expand=True,
            ),
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                icon_color=C.PRIMARY,
                on_click=lambda e: atualizar_ao_clicar(),
            ),
        ],
    )

    # =========================================
    # CONTEÚDO PRINCIPAL
    # =========================================

    conteudo = ft.Column(
        controls=[
            cabecalho,
            filtros,
            campos_personalizados,
            status,
            indicadores,

            ft.Container(height=12),

            ft.Text(
                "Faturamento diário",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=C.TEXT,
            ),
            ft.Text(
                "Evolução das vendas no período selecionado",
                size=12,
                color=C.TEXT_SECONDARY,
            ),

            grafico_diario,

            ft.Container(height=12),

            ft.Text(
                "Produtos mais vendidos",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=C.TEXT,
            ),
            ft.Text(
                "Ranking por quantidade vendida",
                size=12,
                color=C.TEXT_SECONDARY,
            ),

            lista_ranking,
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # =========================================
    # EXIBIR TELA
    # =========================================

    page.clean()
    page.navigation_bar = None
    page.bgcolor = C.BACKGROUND
    page.padding = 16

    page.add(
        ft.SafeArea(
            content=conteudo,
            expand=True,
        )
    )

    atualizar_dashboard(filtro_atual)

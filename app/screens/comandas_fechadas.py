
import flet as ft

from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from app.theme.colors import AppColors as C
from app.services.comandas_service import (
    listar_comandas_fechadas_bd,
    buscar_detalhes_comanda_bd,
)


FUSO = ZoneInfo("America/Sao_Paulo")


def formatar_moeda(valor):
    try:
        numero = Decimal(str(valor or 0))
    except (InvalidOperation, ValueError, TypeError):
        numero = Decimal("0")

    return (
        f"R$ {numero:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def converter_data(data_iso):
    if not data_iso:
        return None

    try:
        if isinstance(data_iso, datetime):
            data = data_iso
        else:
            data = datetime.fromisoformat(
                str(data_iso).replace("Z", "+00:00")
            )

        if data.tzinfo is None:
            data = data.replace(tzinfo=ZoneInfo("UTC"))

        return data.astimezone(FUSO)

    except (ValueError, TypeError, OverflowError):
        return None


def formatar_data(data_iso):
    data = converter_data(data_iso)

    if data is None:
        return "Horário não registrado"

    return data.strftime("%d/%m/%Y às %H:%M")


def comandas_fechadas_screen(
    page,
    voltar,
    abrir_detalhes,
    cliente_supabase,
    usuario=None,
):
    usuario = usuario or {}
    administrador = usuario.get("funcao") == "admin"

    FUNDO = C.BACKGROUND
    SUPERFICIE = C.SURFACE
    AMARELO = C.PRIMARY
    VERMELHO = C.RED
    VERDE = C.GREEN
    TEXTO = C.TEXT
    SECUNDARIO = C.TEXT_SECONDARY
    BORDA = C.BORDER

    # =========================================
    # COMPONENTES AUXILIARES
    # =========================================

    def criar_borda(cor, largura=1):
        lado = ft.BorderSide(
            width=largura,
            color=cor,
        )

        return ft.Border(
            left=lado,
            top=lado,
            right=lado,
            bottom=lado,
        )

    # =========================================
    # CARREGAMENTO DAS COMANDAS
    # =========================================

    erro_carregamento = False

    try:
        registros = listar_comandas_fechadas_bd(
            cliente_supabase
        )

        comandas = []

        for registro in registros:
            detalhes = buscar_detalhes_comanda_bd(
                cliente_supabase,
                registro["id"],
            )

            if detalhes:
                comandas.append(detalhes)

    except Exception as erro:
        print(
            f"Erro ao carregar comandas fechadas: {erro}"
        )

        comandas = []
        erro_carregamento = True

    comandas.sort(
        key=lambda c: (
            converter_data(c.get("fechada_em"))
            or datetime.min.replace(tzinfo=FUSO)
        ),
        reverse=True,
    )

    # =========================================
    # ESTADO DOS FILTROS
    # =========================================

    periodo_atual = "todas"

    lista = ft.Column(spacing=12)

    texto_resultados = ft.Text(
        "",
        size=12,
        color=SECUNDARIO,
    )

    valor_total_texto = ft.Text(
        "R$ 0,00",
        size=22,
        weight=ft.FontWeight.BOLD,
        color=AMARELO,
    )

    quantidade_texto = ft.Text(
        "0",
        size=23,
        weight=ft.FontWeight.BOLD,
        color=TEXTO,
    )

    # =========================================
    # CARTÃO DE COMANDA
    # =========================================

    def criar_card(comanda):
        itens = comanda.get("itens") or []

        quantidade = sum(
            int(item.get("quantidade") or 0)
            for item in itens
        )

        numero = str(comanda["id"]).zfill(2)

        cliente = (
            comanda.get("cliente")
            or "Cliente não informado"
        )

        horario = formatar_data(
            comanda.get("fechada_em")
        )

        return ft.Container(
            bgcolor=SUPERFICIE,
            border=criar_borda(BORDA),
            border_radius=18,
            padding=16,
            on_click=lambda e, c=comanda: abrir_detalhes(c),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                width=52,
                                height=52,
                                bgcolor="#193424",
                                border_radius=14,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(
                                    ft.Icons.CHECK_CIRCLE,
                                    color=VERDE,
                                    size=29,
                                ),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        cliente,
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXTO,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(
                                        f"Comanda #{numero}",
                                        size=12,
                                        color=SECUNDARIO,
                                    ),
                                    ft.Text(
                                        horario,
                                        size=12,
                                        color=SECUNDARIO,
                                    ),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                            ft.Icon(
                                ft.Icons.CHEVRON_RIGHT,
                                size=22,
                                color=AMARELO,
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(
                        color=BORDA,
                        height=16,
                    ),
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(
                                        ft.Icons.SHOPPING_BAG_OUTLINED,
                                        color=SECUNDARIO,
                                        size=16,
                                    ),
                                    ft.Text(
                                        f"{quantidade} "
                                        f"{'item' if quantidade == 1 else 'itens'}",
                                        size=12,
                                        color=SECUNDARIO,
                                    ),
                                ],
                                spacing=6,
                                tight=True,
                            ),
                            ft.Container(
                                bgcolor="#193424",
                                border_radius=20,
                                padding=ft.Padding.symmetric(
                                    horizontal=11,
                                    vertical=6,
                                ),
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.CHECK_CIRCLE,
                                            size=14,
                                            color=VERDE,
                                        ),
                                        ft.Text(
                                            "Finalizada",
                                            size=11,
                                            weight=ft.FontWeight.BOLD,
                                            color=VERDE,
                                        ),
                                    ],
                                    spacing=6,
                                    tight=True,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "TOTAL DA COMANDA",
                                        size=10,
                                        color=SECUNDARIO,
                                    ),
                                    ft.Text(
                                        formatar_moeda(
                                            comanda.get("total")
                                        ),
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color=AMARELO,
                                    ),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                            ft.Button(
                                content=ft.Row(
                                    controls=[
                                        ft.Text(
                                            "Detalhes",
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Icon(
                                            ft.Icons.ARROW_FORWARD,
                                            size=17,
                                        ),
                                    ],
                                    spacing=6,
                                    tight=True,
                                ),
                                bgcolor=AMARELO,
                                color=FUNDO,
                                on_click=lambda e, c=comanda: abrir_detalhes(c),
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=10,
            ),
        )

    # =========================================
    # FILTRO POR PERÍODO
    # =========================================

    def corresponde_periodo(comanda):
        if periodo_atual == "todas":
            return True

        data = converter_data(
            comanda.get("fechada_em")
        )

        if data is None:
            return False

        agora = datetime.now(FUSO)

        if periodo_atual == "hoje":
            return data.date() == agora.date()

        if periodo_atual == "7dias":
            return (
                agora - timedelta(days=7)
                <= data
                <= agora
            )

        if periodo_atual == "30dias":
            return (
                agora - timedelta(days=30)
                <= data
                <= agora
            )

        return True

    # =========================================
    # PESQUISA E ATUALIZAÇÃO
    # =========================================

    def atualizar_lista():
        texto = (
            pesquisa.value or ""
        ).strip().casefold()

        filtradas = [
            comanda
            for comanda in comandas
            if (
                corresponde_periodo(comanda)
                and (
                    texto in str(
                        comanda.get("cliente") or ""
                    ).casefold()
                    or texto in str(
                        comanda.get("id", "")
                    )
                )
            )
        ]

        quantidade = len(filtradas)

        quantidade_texto.value = str(quantidade)

        texto_resultados.value = (
            f"{quantidade} "
            f"{'comanda encontrada' if quantidade == 1 else 'comandas encontradas'}"
        )

        if administrador:
            total = sum(
                (
                    Decimal(
                        str(comanda.get("total") or 0)
                    )
                    for comanda in filtradas
                ),
                Decimal("0"),
            )

            valor_total_texto.value = formatar_moeda(
                total
            )

        lista.controls.clear()

        if erro_carregamento:
            lista.controls.append(
                ft.Container(
                    padding=30,
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.ERROR_OUTLINE,
                                size=46,
                                color=VERMELHO,
                            ),
                            ft.Text(
                                "Não foi possível carregar as comandas.",
                                size=15,
                                color=TEXTO,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Volte e tente novamente.",
                                size=12,
                                color=SECUNDARIO,
                            ),
                        ],
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )

        elif not filtradas:
            lista.controls.append(
                ft.Container(
                    padding=30,
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.INBOX_OUTLINED,
                                size=48,
                                color=AMARELO,
                            ),
                            ft.Text(
                                "Nenhuma comanda encontrada.",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=TEXTO,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Experimente alterar a pesquisa ou o período.",
                                size=12,
                                color=SECUNDARIO,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        spacing=10,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )

        else:
            for comanda in filtradas:
                lista.controls.append(
                    criar_card(comanda)
                )

        page.update()

    # =========================================
    # CAMPO DE PESQUISA
    # =========================================

    pesquisa = ft.TextField(
        hint_text="Buscar cliente ou número da comanda",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=SUPERFICIE,
        border_color=BORDA,
        focused_border_color=AMARELO,
        border_radius=12,
        text_size=14,
        height=54,
        on_change=lambda e: atualizar_lista(),
    )

    # =========================================
    # SELETOR DE PERÍODO
    # =========================================

    opcoes_periodo = [
        ("todas", "Todas"),
        ("hoje", "Hoje"),
        ("7dias", "7 dias"),
        ("30dias", "30 dias"),
    ]

    botoes_periodo = {}

    def atualizar_botoes_periodo():
        for chave, botao in botoes_periodo.items():
            selecionado = chave == periodo_atual

            botao.bgcolor = (
                AMARELO if selecionado else SUPERFICIE
            )

            botao.color = (
                FUNDO if selecionado else SECUNDARIO
            )

    def selecionar_periodo(chave):
        nonlocal periodo_atual

        periodo_atual = chave

        atualizar_botoes_periodo()
        atualizar_lista()

    for chave, titulo in opcoes_periodo:
        botao = ft.Button(
            content=titulo,
            bgcolor=(
                AMARELO if chave == periodo_atual
                else SUPERFICIE
            ),
            color=(
                FUNDO if chave == periodo_atual
                else SECUNDARIO
            ),
            on_click=lambda e, c=chave: selecionar_periodo(c),
        )

        botoes_periodo[chave] = botao

    filtros = ft.Row(
        controls=list(botoes_periodo.values()),
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
    )

    # =========================================
    # INDICADORES
    # =========================================

    indicadores = ft.Column(
        controls=[
            ft.Container(
                bgcolor=SUPERFICIE,
                border=criar_borda(BORDA),
                border_radius=16,
                padding=16,
                content=ft.Row(
                    controls=[
                        ft.Container(
                            width=46,
                            height=46,
                            bgcolor="#193424",
                            border_radius=12,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(
                                ft.Icons.CHECK_CIRCLE,
                                color=VERDE,
                                size=25,
                            ),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "Comandas finalizadas",
                                    size=12,
                                    color=SECUNDARIO,
                                ),
                                quantidade_texto,
                            ],
                            spacing=4,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                ),
            ),
        ],
        spacing=10,
    )

    if administrador:
        indicadores.controls.append(
            ft.Container(
                bgcolor=SUPERFICIE,
                border=criar_borda(BORDA),
                border_radius=16,
                padding=16,
                content=ft.Row(
                    controls=[
                        ft.Container(
                            width=46,
                            height=46,
                            bgcolor=FUNDO,
                            border_radius=12,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Icon(
                                ft.Icons.PAYMENTS_OUTLINED,
                                color=AMARELO,
                                size=25,
                            ),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "Valor total das comandas filtradas",
                                    size=12,
                                    color=SECUNDARIO,
                                ),
                                valor_total_texto,
                            ],
                            spacing=4,
                            expand=True,
                        ),
                    ],
                    spacing=12,
                ),
            )
        )

    # =========================================
    # CABEÇALHO
    # =========================================

    cabecalho = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=TEXTO,
                on_click=lambda e: voltar(),
            ),
            ft.Column(
                controls=[
                    ft.Text(
                        "Comandas fechadas",
                        size=21,
                        weight=ft.FontWeight.BOLD,
                        color=TEXTO,
                    ),
                    ft.Text(
                        "Histórico de pedidos finalizados",
                        size=11,
                        color=SECUNDARIO,
                    ),
                ],
                spacing=3,
                expand=True,
            ),
            ft.Container(
                bgcolor="#193424",
                border_radius=20,
                padding=ft.Padding.symmetric(
                    horizontal=12,
                    vertical=7,
                ),
                content=ft.Text(
                    str(len(comandas)),
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=VERDE,
                ),
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # =========================================
    # CONTEÚDO PRINCIPAL
    # =========================================

    conteudo = ft.Column(
        controls=[
            cabecalho,
            ft.Container(height=8),
            indicadores,
            ft.Container(height=12),
            ft.Text(
                "Histórico de comandas",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=TEXTO,
            ),
            pesquisa,
            filtros,
            texto_resultados,
            lista,
            ft.Container(height=20),
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    page.clean()
    page.navigation_bar = None
    page.drawer = None
    page.bgcolor = FUNDO
    page.padding = 16

    page.add(
        ft.SafeArea(
            expand=True,
            content=conteudo,
        )
    )

    atualizar_lista()

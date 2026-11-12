
import flet as ft

from datetime import datetime
from decimal import Decimal
from time import perf_counter
from zoneinfo import ZoneInfo

from app.theme.colors import AppColors as C
from app.services.comandas_service import (
    listar_comandas_abertas_com_detalhes_bd,
)


# =========================================
# FUNÇÕES AUXILIARES
# =========================================

def formatar_moeda(valor):
    try:
        numero = Decimal(str(valor or 0))
    except (ValueError, TypeError):
        numero = Decimal("0")

    return (
        f"R$ {numero:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def formatar_horario(data_iso):
    if not data_iso:
        return "Horário indisponível"

    try:
        if isinstance(data_iso, datetime):
            data = data_iso
        else:
            data = datetime.fromisoformat(
                str(data_iso).replace("Z", "+00:00")
            )

        if data.tzinfo is None:
            data = data.replace(tzinfo=ZoneInfo("UTC"))

        data = data.astimezone(
            ZoneInfo("America/Sao_Paulo")
        )

        return data.strftime("%d/%m/%Y às %H:%M")

    except (ValueError, TypeError, OverflowError):
        return "Horário indisponível"


# =========================================
# TELA DE COMANDAS ABERTAS
# =========================================

def comandas_abertas_screen(
    page: ft.Page,
    voltar,
    abrir_detalhes,
    abrir_nova,
    cliente_supabase,
    usuario=None,
):
    usuario = usuario or {}
    administrador = usuario.get("funcao") == "admin"

    FUNDO = C.BACKGROUND
    SUPERFICIE = C.SURFACE
    AMARELO = C.PRIMARY
    VERMELHO = C.RED
    TEXTO = C.TEXT
    SECUNDARIO = C.TEXT_SECONDARY
    BORDA = C.BORDER

    # =========================================
    # ACESSIBILIDADE
    # =========================================

    fonte_ampliada = False

    def tamanho_fonte(tamanho_normal):
        if fonte_ampliada:
            return tamanho_normal + 4
        return tamanho_normal

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

    def mensagem(texto):
        page.show_dialog(
            ft.SnackBar(content=ft.Text(texto))
        )

    # =========================================
    # CARREGAMENTO OTIMIZADO DAS COMANDAS
    # =========================================

    erro_carregamento = False
    inicio_carregamento = perf_counter()

    try:
        comandas = listar_comandas_abertas_com_detalhes_bd(
            cliente_supabase
        )

    except Exception as erro:
        print(f"Erro ao carregar comandas: {erro}")
        comandas = []
        erro_carregamento = True

    tempo_carregamento = (
        perf_counter() - inicio_carregamento
    )

    print(
        f"[DESEMPENHO] Carregamento das comandas: "
        f"{tempo_carregamento:.3f} segundos"
    )

    # =========================================
    # INDICADORES
    # =========================================

    quantidade_comandas = len(comandas)

    quantidade_itens = sum(
        sum(
            int(item.get("quantidade", 0))
            for item in (comanda.get("itens") or [])
        )
        for comanda in comandas
    )

    total_aberto = sum(
        (
            Decimal(str(comanda.get("total") or 0))
            for comanda in comandas
        ),
        Decimal("0"),
    )

    def criar_indicador(titulo, valor, icone, cor):
        return ft.Container(
            expand=True,
            bgcolor=SUPERFICIE,
            border=criar_borda(BORDA),
            border_radius=16,
            padding=14,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(
                                icone,
                                size=20,
                                color=cor,
                            ),
                            ft.Text(
                                titulo,
                                size=tamanho_fonte(11),
                                color=SECUNDARIO,
                                expand=True,
                            ),
                        ],
                        spacing=7,
                    ),
                    ft.Text(
                        str(valor),
                        size=tamanho_fonte(20),
                        weight=ft.FontWeight.BOLD,
                        color=TEXTO,
                    ),
                ],
                spacing=9,
            ),
        )

    def criar_indicadores():
        indicadores = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        criar_indicador(
                            "Em aberto",
                            quantidade_comandas,
                            ft.Icons.RECEIPT_LONG,
                            AMARELO,
                        ),
                        criar_indicador(
                            "Itens pedidos",
                            quantidade_itens,
                            ft.Icons.FASTFOOD_OUTLINED,
                            VERMELHO,
                        ),
                    ],
                    spacing=10,
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
                            ft.Icon(
                                ft.Icons.PAYMENTS_OUTLINED,
                                color=AMARELO,
                                size=25,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Valor em comandas abertas",
                                        size=tamanho_fonte(12),
                                        color=SECUNDARIO,
                                    ),
                                    ft.Text(
                                        formatar_moeda(total_aberto),
                                        size=tamanho_fonte(22),
                                        weight=ft.FontWeight.BOLD,
                                        color=AMARELO,
                                    ),
                                ],
                                spacing=4,
                                expand=True,
                            ),
                        ],
                        spacing=12,
                    ),
                )
            )

        return indicadores

    # =========================================
    # CARTÃO DE COMANDA
    # =========================================

    def criar_card(comanda):
        itens = comanda.get("itens") or []

        quantidade = sum(
            int(item.get("quantidade", 0))
            for item in itens
        )

        numero = str(comanda["id"]).zfill(2)

        cliente = (
            comanda.get("cliente")
            or "Cliente não informado"
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
                                width=62 if fonte_ampliada else 54,
                                height=62 if fonte_ampliada else 54,
                                bgcolor=FUNDO,
                                border=criar_borda(AMARELO),
                                border_radius=14,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(
                                    numero,
                                    size=tamanho_fonte(19),
                                    weight=ft.FontWeight.BOLD,
                                    color=AMARELO,
                                ),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        cliente,
                                        size=tamanho_fonte(16),
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXTO,
                                        max_lines=(
                                            2 if fonte_ampliada else 1
                                        ),
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(
                                        formatar_horario(
                                            comanda.get("aberta_em")
                                        ),
                                        size=tamanho_fonte(12),
                                        color=SECUNDARIO,
                                    ),
                                ],
                                spacing=5,
                                expand=True,
                            ),
                            ft.Icon(
                                ft.Icons.CHEVRON_RIGHT,
                                color=AMARELO,
                                size=24,
                            ),
                        ],
                        spacing=12,
                        vertical_alignment=(
                            ft.CrossAxisAlignment.CENTER
                        ),
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
                                        size=16,
                                        color=SECUNDARIO,
                                    ),
                                    ft.Text(
                                        f"{quantidade} "
                                        f"{'item' if quantidade == 1 else 'itens'}",
                                        size=tamanho_fonte(12),
                                        color=SECUNDARIO,
                                    ),
                                ],
                                spacing=6,
                                tight=True,
                            ),
                            ft.Container(
                                bgcolor=FUNDO,
                                border_radius=20,
                                padding=ft.Padding.symmetric(
                                    horizontal=11,
                                    vertical=6,
                                ),
                                content=ft.Row(
                                    controls=[
                                        ft.Container(
                                            width=7,
                                            height=7,
                                            bgcolor=VERMELHO,
                                            border_radius=4,
                                        ),
                                        ft.Text(
                                            "Em aberto",
                                            size=tamanho_fonte(11),
                                            weight=ft.FontWeight.BOLD,
                                            color=TEXTO,
                                        ),
                                    ],
                                    spacing=6,
                                    tight=True,
                                ),
                            ),
                        ],
                        alignment=(
                            ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                    ),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "TOTAL DA COMANDA",
                                        size=tamanho_fonte(10),
                                        color=SECUNDARIO,
                                    ),
                                    ft.Text(
                                        formatar_moeda(
                                            comanda.get("total")
                                        ),
                                        size=tamanho_fonte(21),
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
                                            size=tamanho_fonte(14),
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
                                on_click=(
                                    lambda e, c=comanda:
                                    abrir_detalhes(c)
                                ),
                            ),
                        ],
                        vertical_alignment=(
                            ft.CrossAxisAlignment.CENTER
                        ),
                    ),
                ],
                spacing=10,
            ),
        )

    # =========================================
    # PESQUISA
    # =========================================

    lista = ft.Column(spacing=12)

    quantidade_resultados = ft.Text(
        "",
        size=tamanho_fonte(12),
        color=SECUNDARIO,
    )

    def atualizar_lista(
        texto="",
        atualizar_pagina=True,
    ):
        texto = (texto or "").strip().casefold()

        filtradas = [
            comanda
            for comanda in comandas
            if (
                texto in str(
                    comanda.get("cliente") or ""
                ).casefold()
                or texto in str(
                    comanda.get("id", "")
                )
            )
        ]

        lista.controls.clear()

        quantidade_resultados.value = (
            f"{len(filtradas)} "
            f"{'comanda encontrada' if len(filtradas) == 1 else 'comandas encontradas'}"
        )

        quantidade_resultados.size = tamanho_fonte(12)

        if erro_carregamento:
            lista.controls.append(
                ft.Container(
                    padding=25,
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.ERROR_OUTLINE,
                                color=VERMELHO,
                                size=40,
                            ),
                            ft.Text(
                                "Não foi possível carregar as comandas.",
                                size=tamanho_fonte(14),
                                color=TEXTO,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Volte à tela inicial e tente novamente.",
                                size=tamanho_fonte(12),
                                color=SECUNDARIO,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=(
                            ft.CrossAxisAlignment.CENTER
                        ),
                        spacing=10,
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
                                (
                                    "Nenhuma comanda em aberto."
                                    if not texto
                                    else "Nenhuma comanda encontrada."
                                ),
                                size=tamanho_fonte(16),
                                weight=ft.FontWeight.BOLD,
                                color=TEXTO,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                (
                                    "Crie um novo pedido para começar."
                                    if not texto
                                    else "Tente pesquisar outro nome ou número."
                                ),
                                size=tamanho_fonte(12),
                                color=SECUNDARIO,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=(
                            ft.CrossAxisAlignment.CENTER
                        ),
                        spacing=10,
                    ),
                )
            )

        else:
            for comanda in filtradas:
                lista.controls.append(
                    criar_card(comanda)
                )

        if atualizar_pagina:
            page.update()

    pesquisa = ft.TextField(
        hint_text="Buscar cliente ou número da comanda",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=SUPERFICIE,
        border_color=BORDA,
        focused_border_color=AMARELO,
        border_radius=12,
        text_size=tamanho_fonte(14),
        height=62 if fonte_ampliada else 54,
        on_change=(
            lambda e: atualizar_lista(e.control.value)
        ),
    )

    # =========================================
    # CABEÇALHO
    # =========================================

    titulo_cabecalho = ft.Text(
        "Comandas abertas",
        size=tamanho_fonte(21),
        weight=ft.FontWeight.BOLD,
        color=TEXTO,
    )

    subtitulo_cabecalho = ft.Text(
        "Acompanhe os pedidos em andamento",
        size=tamanho_fonte(11),
        color=SECUNDARIO,
    )

    contador_cabecalho = ft.Text(
        str(quantidade_comandas),
        color=TEXTO,
        weight=ft.FontWeight.BOLD,
        size=tamanho_fonte(13),
    )

    botao_acessibilidade = ft.IconButton(
        icon=ft.Icons.TEXT_INCREASE,
        icon_color=AMARELO,
        tooltip="Aumentar tamanho das letras",
    )

    cabecalho = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=TEXTO,
                on_click=lambda e: voltar(),
            ),
            ft.Column(
                controls=[
                    titulo_cabecalho,
                    subtitulo_cabecalho,
                ],
                spacing=3,
                expand=True,
            ),
            botao_acessibilidade,
            ft.Container(
                bgcolor=VERMELHO,
                border_radius=20,
                padding=ft.Padding.symmetric(
                    horizontal=12,
                    vertical=7,
                ),
                content=contador_cabecalho,
            ),
        ],
        vertical_alignment=(
            ft.CrossAxisAlignment.CENTER
        ),
    )

    # =========================================
    # BOTÃO NOVA COMANDA
    # =========================================

    texto_nova_comanda = ft.Text(
        "Nova comanda",
        size=tamanho_fonte(16),
        weight=ft.FontWeight.BOLD,
    )

    botao_nova = ft.Button(
        content=ft.Row(
            controls=[
                ft.Icon(
                    ft.Icons.ADD_CIRCLE_OUTLINE,
                    size=21,
                ),
                texto_nova_comanda,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        bgcolor=AMARELO,
        color=FUNDO,
        height=64 if fonte_ampliada else 56,
        width=float("inf"),
        on_click=lambda e: abrir_nova(),
    )

    # =========================================
    # CONTEÚDO DA TELA
    # =========================================

    titulo_pedidos = ft.Text(
        "Pedidos em andamento",
        size=tamanho_fonte(18),
        weight=ft.FontWeight.BOLD,
        color=TEXTO,
    )

    conteudo = ft.Column(
        controls=[
            cabecalho,
            ft.Container(height=8),
            criar_indicadores(),
            ft.Container(height=12),
            titulo_pedidos,
            pesquisa,
            quantidade_resultados,
            lista,
            ft.Container(height=20),
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # =========================================
    # ATIVAR / DESATIVAR ACESSIBILIDADE
    # =========================================

    def alternar_fonte(e):
        nonlocal fonte_ampliada

        fonte_ampliada = not fonte_ampliada

        titulo_cabecalho.size = tamanho_fonte(21)
        subtitulo_cabecalho.size = tamanho_fonte(11)
        contador_cabecalho.size = tamanho_fonte(13)

        pesquisa.text_size = tamanho_fonte(14)
        pesquisa.height = (
            62 if fonte_ampliada else 54
        )

        titulo_pedidos.size = tamanho_fonte(18)

        texto_nova_comanda.size = tamanho_fonte(16)
        botao_nova.height = (
            64 if fonte_ampliada else 56
        )

        # Recria os indicadores sem consultar o banco.
        conteudo.controls[2] = criar_indicadores()

        # Mantém o filtro de pesquisa atual.
        atualizar_lista(
            pesquisa.value or "",
            atualizar_pagina=False,
        )

        if fonte_ampliada:
            botao_acessibilidade.icon = (
                ft.Icons.TEXT_DECREASE
            )
            botao_acessibilidade.tooltip = (
                "Restaurar tamanho das letras"
            )
        else:
            botao_acessibilidade.icon = (
                ft.Icons.TEXT_INCREASE
            )
            botao_acessibilidade.tooltip = (
                "Aumentar tamanho das letras"
            )

        page.update()

    botao_acessibilidade.on_click = alternar_fonte

    # =========================================
    # EXIBIR TELA
    # =========================================

    page.clean()
    page.bgcolor = FUNDO
    page.padding = 16
    page.navigation_bar = None
    page.drawer = None

    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Column(
                controls=[
                    conteudo,
                    botao_nova,
                ],
                spacing=12,
                expand=True,
            ),
        )
    )

    atualizar_lista()

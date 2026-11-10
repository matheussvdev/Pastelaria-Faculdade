
import flet as ft
import unicodedata

from datetime import datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from app.theme.colors import AppColors as C
from app.services.comandas_service import fechar_comanda_bd


FUSO = ZoneInfo("America/Sao_Paulo")


# =========================================
# FUNÇÕES AUXILIARES
# =========================================

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


def formatar_data(data_iso):
    if not data_iso:
        return "Data indisponível"

    try:
        if isinstance(data_iso, datetime):
            data = data_iso
        else:
            data = datetime.fromisoformat(
                str(data_iso).replace("Z", "+00:00")
            )

        if data.tzinfo is None:
            data = data.replace(tzinfo=FUSO)
        else:
            data = data.astimezone(FUSO)

        return data.strftime("%d/%m/%Y às %H:%M")

    except (ValueError, TypeError, OverflowError):
        return "Data indisponível"


def normalizar_texto(texto):
    texto = str(texto or "").casefold()

    return "".join(
        caractere
        for caractere in unicodedata.normalize(
            "NFD", texto
        )
        if unicodedata.category(caractere) != "Mn"
    )


def identificar_icone_produto(nome):
    nome = normalizar_texto(nome)

    if "agua" in nome:
        return ft.Icons.WATER_DROP, "#38BDF8"

    refrigerantes = (
        "refrigerante",
        "coca",
        "guarana",
        "fanta",
        "sprite",
        "pepsi",
        "soda",
    )

    if any(palavra in nome for palavra in refrigerantes):
        return ft.Icons.LOCAL_DRINK, "#EF4444"

    if "suco" in nome or "vitamina" in nome:
        return ft.Icons.LOCAL_BAR, "#22C55E"

    if "cafe" in nome or "cappuccino" in nome:
        return ft.Icons.COFFEE, "#D6A56D"

    sabores_pastel = (
        "pastel",
        "carne",
        "queijo",
        "frango",
        "pizza",
        "calabresa",
        "palmito",
        "brocolis",
        "bacalhau",
        "camarao",
        "chocolate",
        "banana",
        "doce de leite",
        "romeu e julieta",
        "portuguesa",
        "quatro queijos",
        "4 queijos",
    )

    if any(sabor in nome for sabor in sabores_pastel):
        return ft.Icons.BAKERY_DINING, C.PRIMARY

    return ft.Icons.RESTAURANT, C.PRIMARY


def criar_borda(cor, largura=1):
    return ft.Border(
        left=ft.BorderSide(width=largura, color=cor),
        top=ft.BorderSide(width=largura, color=cor),
        right=ft.BorderSide(width=largura, color=cor),
        bottom=ft.BorderSide(width=largura, color=cor),
    )


# =========================================
# TELA DE DETALHES DA COMANDA
# =========================================

def detalhes_comanda_screen(
    page,
    comanda,
    voltar,
    atualizar,
    adicionar_itens,
    cliente_supabase,
):
    FUNDO = C.BACKGROUND
    SUPERFICIE = C.SURFACE
    AMARELO = C.PRIMARY
    VERMELHO = C.RED
    VERDE = C.GREEN
    TEXTO = C.TEXT
    SECUNDARIO = C.TEXT_SECONDARY
    BORDA = C.BORDER

    fechada = comanda.get("status") == "fechada"
    fechando = False

    numero_comanda = comanda.get("id")
    nome_cliente = str(
        comanda.get("cliente") or "Cliente não informado"
    )

    try:
        numero_formatado = f"{int(numero_comanda):02d}"
    except (ValueError, TypeError):
        numero_formatado = str(numero_comanda or "--")

    itens_comanda = comanda.get("itens") or []

    quantidade_total = sum(
        int(item.get("quantidade") or 0)
        for item in itens_comanda
    )

    total_comanda = comanda.get("total") or 0

    texto_abertura = formatar_data(
        comanda.get("aberta_em")
    )

    texto_fechamento = formatar_data(
        comanda.get("fechada_em")
    )

    # =========================================
    # MENSAGENS
    # =========================================

    def mostrar_mensagem(texto):
        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(texto)
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
                        f"Comanda #{numero_formatado}",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=TEXTO,
                    ),
                    ft.Text(
                        "Detalhes do pedido",
                        size=12,
                        color=SECUNDARIO,
                    ),
                ],
                spacing=3,
                expand=True,
            ),
            ft.Container(
                width=44,
                height=44,
                bgcolor=SUPERFICIE,
                border_radius=13,
                alignment=ft.Alignment.CENTER,
                content=ft.Icon(
                    ft.Icons.RECEIPT_LONG,
                    color=AMARELO,
                    size=24,
                ),
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # =========================================
    # STATUS DA COMANDA
    # =========================================

    cor_status = VERDE if fechada else AMARELO

    status_comanda = ft.Container(
        bgcolor=SUPERFICIE,
        border=criar_borda(BORDA),
        border_radius=12,
        padding=12,
        content=ft.Row(
            controls=[
                ft.Icon(
                    ft.Icons.CHECK_CIRCLE
                    if fechada
                    else ft.Icons.SCHEDULE,
                    color=cor_status,
                    size=21,
                ),
                ft.Text(
                    "Comanda finalizada"
                    if fechada
                    else "Comanda em aberto",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=cor_status,
                ),
            ],
            spacing=10,
        ),
    )

    # =========================================
    # INFORMAÇÕES DO CLIENTE
    # =========================================

    informacoes_cliente = [
        ft.Row(
            controls=[
                ft.Container(
                    width=46,
                    height=46,
                    bgcolor=FUNDO,
                    border_radius=13,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(
                        ft.Icons.PERSON_OUTLINE,
                        color=AMARELO,
                        size=25,
                    ),
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            "CLIENTE",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=SECUNDARIO,
                        ),
                        ft.Text(
                            nome_cliente,
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=TEXTO,
                        ),
                    ],
                    spacing=4,
                    expand=True,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        ft.Divider(color=BORDA),
        ft.Row(
            controls=[
                ft.Icon(
                    ft.Icons.CALENDAR_TODAY,
                    size=17,
                    color=SECUNDARIO,
                ),
                ft.Text(
                    f"Abertura: {texto_abertura}",
                    size=12,
                    color=SECUNDARIO,
                    expand=True,
                ),
            ],
            spacing=10,
        ),
    ]

    if fechada:
        informacoes_cliente.append(
            ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE_OUTLINE,
                        size=17,
                        color=VERDE,
                    ),
                    ft.Text(
                        f"Fechamento: {texto_fechamento}",
                        size=12,
                        color=SECUNDARIO,
                        expand=True,
                    ),
                ],
                spacing=10,
            )
        )

    cartao_cliente = ft.Container(
        bgcolor=SUPERFICIE,
        border=criar_borda(BORDA),
        border_radius=16,
        padding=16,
        content=ft.Column(
            controls=informacoes_cliente,
            spacing=12,
        ),
    )

    # =========================================
    # CARTÕES DE PRODUTOS
    # =========================================

    def criar_item(item):
        nome = str(item.get("nome") or "Produto")

        quantidade = int(
            item.get("quantidade") or 0
        )

        preco = item.get("preco_unitario") or 0
        subtotal = item.get("subtotal") or 0

        icone_produto, cor_icone = (
            identificar_icone_produto(nome)
        )

        return ft.Container(
            bgcolor=SUPERFICIE,
            border=criar_borda(BORDA),
            border_radius=15,
            padding=14,
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=44,
                        height=44,
                        bgcolor=FUNDO,
                        border_radius=12,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(
                            icone_produto,
                            color=cor_icone,
                            size=24,
                        ),
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                nome,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=TEXTO,
                                max_lines=2,
                            ),
                            ft.Text(
                                (
                                    f"{quantidade} x "
                                    f"{formatar_moeda(preco)}"
                                ),
                                size=12,
                                color=SECUNDARIO,
                            ),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                "SUBTOTAL",
                                size=10,
                                color=SECUNDARIO,
                            ),
                            ft.Text(
                                formatar_moeda(subtotal),
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=AMARELO,
                            ),
                        ],
                        spacing=5,
                        horizontal_alignment=(
                            ft.CrossAxisAlignment.END
                        ),
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    lista_itens = [
        criar_item(item)
        for item in itens_comanda
    ]

    if not lista_itens:
        lista_itens = [
            ft.Container(
                bgcolor=SUPERFICIE,
                border=criar_borda(BORDA),
                border_radius=15,
                padding=30,
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.RESTAURANT_MENU,
                            size=42,
                            color=AMARELO,
                        ),
                        ft.Text(
                            "Nenhum produto registrado.",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color=TEXTO,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Adicione produtos para iniciar o pedido."
                            if not fechada
                            else "Esta comanda não possui itens.",
                            size=12,
                            color=SECUNDARIO,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    spacing=10,
                    horizontal_alignment=(
                        ft.CrossAxisAlignment.CENTER
                    ),
                ),
            )
        ]

    secao_produtos = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(
                        "Produtos do pedido",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEXTO,
                        expand=True,
                    ),
                    ft.Container(
                        bgcolor=SUPERFICIE,
                        border_radius=10,
                        padding=10,
                        content=ft.Text(
                            f"{len(itens_comanda)} "
                            f"{'produto' if len(itens_comanda) == 1 else 'produtos'}",
                            size=12,
                            color=AMARELO,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            *lista_itens,
        ],
        spacing=10,
    )

    # =========================================
    # RESUMO FINANCEIRO
    # =========================================

    resumo = ft.Container(
        bgcolor=SUPERFICIE,
        border=criar_borda(BORDA),
        border_radius=18,
        padding=16,
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "RESUMO DA COMANDA",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=SECUNDARIO,
                        ),
                        ft.Icon(
                            ft.Icons.RECEIPT,
                            size=20,
                            color=AMARELO,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Quantidade de itens",
                            size=13,
                            color=SECUNDARIO,
                        ),
                        ft.Text(
                            str(quantidade_total),
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=TEXTO,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(color=BORDA),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Total da comanda",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=TEXTO,
                        ),
                        ft.Text(
                            formatar_moeda(total_comanda),
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=AMARELO,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=12,
        ),
    )

    # =========================================
    # FECHAMENTO DA COMANDA
    # =========================================

    def confirmar_fechamento(e):
        nonlocal fechando

        if comanda.get("status") != "aberta":
            return

        if fechando:
            return

        fechando = True
        botao_confirmar_fechamento.disabled = True
        page.update()

        try:
            total_fechado = fechar_comanda_bd(
                cliente_supabase,
                int(comanda["id"]),
            )

        except Exception as erro:
            print(f"Erro ao fechar comanda: {erro}")

            fechando = False
            botao_confirmar_fechamento.disabled = False

            page.pop_dialog()

            mostrar_mensagem(
                "Não foi possível fechar a comanda. "
                "Verifique a conexão e tente novamente."
            )
            return

        comanda["status"] = "fechada"
        comanda["total"] = total_fechado

        page.pop_dialog()

        atualizar()

        mostrar_mensagem(
            "Comanda fechada com sucesso! "
            f"Total: {formatar_moeda(total_fechado)}"
        )

    def solicitar_fechamento(e):
        if comanda.get("status") != "aberta":
            return

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                bgcolor=SUPERFICIE,
                title=ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.RECEIPT_LONG,
                            color=AMARELO,
                            size=25,
                        ),
                        ft.Text(
                            "Fechar comanda?",
                            size=19,
                            weight=ft.FontWeight.BOLD,
                            color=TEXTO,
                        ),
                    ],
                    spacing=10,
                ),
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Confirme os dados antes de finalizar:",
                            size=13,
                            color=SECUNDARIO,
                        ),
                        ft.Text(
                            f"Cliente: {nome_cliente}",
                            size=14,
                            color=TEXTO,
                        ),
                        ft.Text(
                            f"Comanda: #{numero_formatado}",
                            size=14,
                            color=TEXTO,
                        ),
                        ft.Divider(color=BORDA),
                        ft.Text(
                            "VALOR TOTAL",
                            size=11,
                            color=SECUNDARIO,
                        ),
                        ft.Text(
                            formatar_moeda(total_comanda),
                            size=25,
                            weight=ft.FontWeight.BOLD,
                            color=AMARELO,
                        ),
                        ft.Text(
                            "Após o fechamento, não será possível "
                            "adicionar novos produtos.",
                            size=12,
                            color=VERMELHO,
                        ),
                    ],
                    spacing=10,
                    tight=True,
                ),
                actions=[
                    ft.TextButton(
                        content="Cancelar",
                        on_click=lambda e: page.pop_dialog(),
                    ),
                    botao_confirmar_fechamento,
                ],
                actions_alignment=(
                    ft.MainAxisAlignment.END
                ),
            )
        )

    botao_confirmar_fechamento = ft.Button(
        content="Confirmar fechamento",
        bgcolor=AMARELO,
        color=FUNDO,
        on_click=confirmar_fechamento,
    )

    # =========================================
    # BOTÕES DE AÇÃO
    # =========================================

    botoes = ft.Column(
        controls=[
            ft.Button(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.ADD_CIRCLE_OUTLINE,
                            size=21,
                        ),
                        ft.Text(
                            "Adicionar mais itens",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                    spacing=9,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                bgcolor=AMARELO,
                color=FUNDO,
                height=54,
                width=float("inf"),
                visible=not fechada,
                on_click=lambda e: adicionar_itens(),
            ),
            ft.OutlinedButton(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE_OUTLINE,
                            color=VERMELHO,
                            size=20,
                        ),
                        ft.Text(
                            "Fechar comanda",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color=VERMELHO,
                        ),
                    ],
                    spacing=9,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                height=54,
                width=float("inf"),
                visible=not fechada,
                on_click=solicitar_fechamento,
            ),
        ],
        spacing=12,
    )

    if fechada:
        botoes.controls.append(
            ft.Container(
                bgcolor=SUPERFICIE,
                border=criar_borda(BORDA),
                border_radius=14,
                padding=14,
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.VERIFIED,
                            color=VERDE,
                            size=22,
                        ),
                        ft.Text(
                            "Esta comanda foi finalizada.",
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=VERDE,
                            expand=True,
                        ),
                    ],
                    spacing=10,
                ),
            )
        )

    # =========================================
    # CONTEÚDO PRINCIPAL
    # =========================================

    conteudo = ft.Column(
        controls=[
            cabecalho,
            status_comanda,
            cartao_cliente,
            secao_produtos,
            resumo,
            botoes,
            ft.Container(height=15),
        ],
        spacing=16,
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
            content=conteudo,
            expand=True,
        )
    )

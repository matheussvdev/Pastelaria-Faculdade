
import flet as ft
from decimal import Decimal, InvalidOperation
import unicodedata

from app.theme.colors import AppColors as C


def nova_comanda_screen(
    page,
    voltar,
    salvar,
    comanda=None,
    cardapio=None,
):
    cardapio = cardapio or []
    editando = comanda is not None

    FUNDO = C.BACKGROUND
    SUPERFICIE = C.SURFACE
    AMARELO = C.PRIMARY
    TEXTO = C.TEXT
    SECUNDARIO = C.TEXT_SECONDARY
    BORDA = C.BORDER

    quantidades = {
        produto["id"]: 0
        for produto in cardapio
    }

    textos_quantidade = {}
    salvando = False

    # =========================================
    # FUNÇÕES AUXILIARES
    # =========================================

    def criar_borda(cor, largura=1):
        return ft.Border(
            left=ft.BorderSide(width=largura, color=cor),
            top=ft.BorderSide(width=largura, color=cor),
            right=ft.BorderSide(width=largura, color=cor),
            bottom=ft.BorderSide(width=largura, color=cor),
        )

    def converter_preco(valor):
        try:
            return Decimal(str(valor or 0))
        except (InvalidOperation, ValueError, TypeError):
            return Decimal("0")

    def formatar_moeda(valor):
        numero = converter_preco(valor)

        return (
            f"R$ {numero:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def normalizar_texto(texto):
        texto = str(texto or "").casefold()

        return "".join(
            caractere
            for caractere in unicodedata.normalize(
                "NFD", texto
            )
            if unicodedata.category(caractere) != "Mn"
        )

    def mostrar_erro(texto):
        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(texto)
            )
        )

    # =========================================
    # IDENTIFICAÇÃO DINÂMICA DE ÍCONES
    # =========================================

    def identificar_icone_produto(nome):
        nome = normalizar_texto(nome)

        # Água
        if "agua" in nome:
            return ft.Icons.WATER_DROP, "#38BDF8"

        # Refrigerantes
        if any(
            palavra in nome
            for palavra in (
                "refrigerante",
                "coca",
                "guarana",
                "fanta",
                "sprite",
                "pepsi",
                "soda",
            )
        ):
            return ft.Icons.LOCAL_DRINK, "#EF4444"

        # Sucos
        if any(
            palavra in nome
            for palavra in ("suco", "vitamina")
        ):
            return ft.Icons.LOCAL_BAR, "#22C55E"

        # Café
        if "cafe" in nome or "cappuccino" in nome:
            return ft.Icons.COFFEE, "#D6A56D"

        # Pastéis e sabores de pastéis
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

        if any(
            sabor in nome
            for sabor in sabores_pastel
        ):
            return ft.Icons.BAKERY_DINING, AMARELO

        # Outros produtos
        return ft.Icons.RESTAURANT, AMARELO

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
                        "Adicionar itens"
                        if editando
                        else "Nova comanda",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=TEXTO,
                    ),
                    ft.Text(
                        "Selecione os produtos do pedido",
                        size=11,
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
    # IDENTIFICAÇÃO DO CLIENTE
    # =========================================

    nome_cliente = ft.TextField(
        label="Nome do cliente",
        hint_text="Digite o nome do cliente",
        value=(
            str(comanda.get("cliente") or "")
            if editando
            else ""
        ),
        disabled=editando,
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        bgcolor=SUPERFICIE,
        border_color=BORDA,
        focused_border_color=AMARELO,
        border_radius=12,
        text_size=14,
        height=60,
    )

    identificacao = ft.Column(
        controls=[
            ft.Text(
                "Identificação do pedido",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=TEXTO,
            ),
            nome_cliente,
        ],
        spacing=12,
    )

    if editando:
        identificacao.controls.append(
            ft.Text(
                "O nome do cliente não pode ser alterado nesta etapa.",
                size=11,
                color=SECUNDARIO,
            )
        )

    # =========================================
    # INDICADORES DO PEDIDO
    # =========================================

    texto_quantidade_total = ft.Text(
        "0",
        size=20,
        weight=ft.FontWeight.BOLD,
        color=TEXTO,
    )

    texto_total = ft.Text(
        "R$ 0,00",
        size=24,
        weight=ft.FontWeight.BOLD,
        color=AMARELO,
    )

    texto_produtos_selecionados = ft.Text(
        "Nenhum produto selecionado",
        size=11,
        color=SECUNDARIO,
    )

    # =========================================
    # ATUALIZAÇÃO DAS QUANTIDADES
    # =========================================

    def atualizar_total():
        total = sum(
            (
                converter_preco(produto.get("preco"))
                * quantidades[produto["id"]]
                for produto in cardapio
            ),
            Decimal("0"),
        )

        quantidade_total = sum(quantidades.values())

        produtos_diferentes = sum(
            1
            for quantidade in quantidades.values()
            if quantidade > 0
        )

        texto_total.value = formatar_moeda(total)
        texto_quantidade_total.value = str(
            quantidade_total
        )

        if produtos_diferentes == 0:
            texto_produtos_selecionados.value = (
                "Nenhum produto selecionado"
            )
        else:
            texto_produtos_selecionados.value = (
                f"{produtos_diferentes} "
                f"{'produto selecionado' if produtos_diferentes == 1 else 'produtos selecionados'}"
            )

        page.update()

    def alterar_quantidade(produto_id, diferenca):
        quantidades[produto_id] = max(
            0,
            quantidades[produto_id] + diferenca,
        )

        if produto_id in textos_quantidade:
            textos_quantidade[produto_id].value = str(
                quantidades[produto_id]
            )

        atualizar_total()

    # =========================================
    # CARTÕES DE PRODUTOS
    # =========================================

    def criar_linha_produto(produto):
        produto_id = produto["id"]

        icone_produto, cor_icone = (
            identificar_icone_produto(
                produto.get("nome")
            )
        )

        texto_quantidade = ft.Text(
            str(quantidades[produto_id]),
            size=17,
            weight=ft.FontWeight.BOLD,
            color=TEXTO,
            width=25,
            text_align=ft.TextAlign.CENTER,
        )

        textos_quantidade[produto_id] = texto_quantidade

        controle_quantidade = ft.Row(
            controls=[
                ft.Container(
                    width=36,
                    height=36,
                    bgcolor=FUNDO,
                    border=criar_borda(BORDA),
                    border_radius=10,
                    alignment=ft.Alignment.CENTER,
                    on_click=lambda e, pid=produto_id: (
                        alterar_quantidade(pid, -1)
                    ),
                    content=ft.Icon(
                        ft.Icons.REMOVE,
                        size=19,
                        color=TEXTO,
                    ),
                ),
                texto_quantidade,
                ft.Container(
                    width=36,
                    height=36,
                    bgcolor=AMARELO,
                    border_radius=10,
                    alignment=ft.Alignment.CENTER,
                    on_click=lambda e, pid=produto_id: (
                        alterar_quantidade(pid, 1)
                    ),
                    content=ft.Icon(
                        ft.Icons.ADD,
                        size=20,
                        color=FUNDO,
                    ),
                ),
            ],
            spacing=8,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        return ft.Container(
            bgcolor=SUPERFICIE,
            border=criar_borda(BORDA),
            border_radius=16,
            padding=14,
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=45,
                        height=45,
                        bgcolor=FUNDO,
                        border_radius=12,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(
                            icone_produto,
                            size=25,
                            color=cor_icone,
                        ),
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                str(
                                    produto.get("nome")
                                    or "Produto"
                                ),
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=TEXTO,
                                max_lines=2,
                            ),
                            ft.Text(
                                formatar_moeda(
                                    produto.get("preco")
                                ),
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=AMARELO,
                            ),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                    controle_quantidade,
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    # =========================================
    # PESQUISA DE PRODUTOS
    # =========================================

    lista_produtos = ft.Column(
        spacing=10,
    )

    texto_resultados = ft.Text(
        "",
        size=12,
        color=SECUNDARIO,
    )

    def atualizar_produtos(texto=""):
        busca = normalizar_texto(texto).strip()

        produtos_filtrados = [
            produto
            for produto in cardapio
            if busca in normalizar_texto(
                produto.get("nome")
            )
        ]

        lista_produtos.controls.clear()

        quantidade_encontrada = len(
            produtos_filtrados
        )

        texto_resultados.value = (
            f"{quantidade_encontrada} "
            f"{'produto disponível' if quantidade_encontrada == 1 else 'produtos disponíveis'}"
        )

        if not produtos_filtrados:
            lista_produtos.controls.append(
                ft.Container(
                    padding=30,
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.SEARCH_OFF,
                                size=42,
                                color=AMARELO,
                            ),
                            ft.Text(
                                "Nenhum produto encontrado.",
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=TEXTO,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Experimente pesquisar outro nome."
                                if cardapio
                                else "Nenhum produto disponível no cardápio.",
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
            )
        else:
            for produto in produtos_filtrados:
                lista_produtos.controls.append(
                    criar_linha_produto(produto)
                )

        page.update()

    pesquisa = ft.TextField(
        hint_text="Buscar produto no cardápio...",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=SUPERFICIE,
        border_color=BORDA,
        focused_border_color=AMARELO,
        border_radius=12,
        text_size=14,
        height=52,
        on_change=lambda e: atualizar_produtos(
            e.control.value
        ),
    )

    secao_produtos = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(
                        "Selecione os produtos",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=TEXTO,
                    ),
                    ft.Icon(
                        ft.Icons.RESTAURANT_MENU,
                        color=AMARELO,
                        size=22,
                    ),
                ],
                alignment=(
                    ft.MainAxisAlignment.SPACE_BETWEEN
                ),
            ),
            pesquisa,
            texto_resultados,
            lista_produtos,
        ],
        spacing=12,
    )

    # =========================================
    # CONFIRMAÇÃO DO PEDIDO
    # =========================================

    def confirmar(e):
        nonlocal salvando

        if salvando:
            return

        nome = (nome_cliente.value or "").strip()

        if not nome:
            mostrar_erro(
                "Informe o nome do cliente."
            )
            return

        itens = []

        for produto in cardapio:
            quantidade = quantidades[produto["id"]]

            if quantidade > 0:
                itens.append({
                    "produto_id": produto["id"],
                    "quantidade": quantidade,
                })

        if not itens:
            mostrar_erro(
                "Selecione pelo menos um produto."
            )
            return

        salvando = True
        botao_confirmar.disabled = True
        page.update()

        try:
            salvar(nome, itens)

        except Exception as erro:
            print(
                f"Erro ao salvar itens: {erro}"
            )

            mostrar_erro(
                "Não foi possível salvar os produtos. "
                "Verifique o terminal."
            )

            salvando = False
            botao_confirmar.disabled = False
            page.update()

    # =========================================
    # RESUMO FIXO DO PEDIDO
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
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "RESUMO DO PEDIDO",
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=SECUNDARIO,
                                ),
                                texto_produtos_selecionados,
                            ],
                            spacing=5,
                            expand=True,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "ITENS",
                                    size=10,
                                    color=SECUNDARIO,
                                ),
                                texto_quantidade_total,
                            ],
                            spacing=3,
                            horizontal_alignment=(
                                ft.CrossAxisAlignment.END
                            ),
                        ),
                    ],
                    alignment=(
                        ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                ),
                ft.Divider(color=BORDA),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Total selecionado",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=TEXTO,
                        ),
                        texto_total,
                    ],
                    alignment=(
                        ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                ),
            ],
            spacing=9,
        ),
    )

    botao_confirmar = ft.Button(
        content=ft.Row(
            controls=[
                ft.Icon(
                    ft.Icons.CHECK_CIRCLE_OUTLINE,
                    size=21,
                ),
                ft.Text(
                    "Adicionar produtos"
                    if editando
                    else "Criar comanda",
                    size=16,
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
        on_click=confirmar,
    )

    rodape = ft.Column(
        controls=[
            resumo,
            botao_confirmar,
        ],
        spacing=10,
    )

    # =========================================
    # CONTEÚDO PRINCIPAL
    # =========================================

    conteudo = ft.Column(
        controls=[
            cabecalho,
            ft.Container(height=8),
            identificacao,
            ft.Container(height=12),
            secao_produtos,
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
            content=ft.Column(
                controls=[
                    conteudo,
                    rodape,
                ],
                spacing=12,
                expand=True,
            ),
        )
    )

    atualizar_produtos()

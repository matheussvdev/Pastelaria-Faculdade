
import flet as ft

from app.theme.colors import AppColors as C


def nova_comanda_screen(
    page,
    voltar,
    salvar,
    comanda=None,
    cardapio=None,
):
    if cardapio is None:
        cardapio = []

    editando = comanda is not None

    quantidades = {
        produto["id"]: 0
        for produto in cardapio
    }

    textos_quantidade = {}
    salvando = False

    def mostrar_erro(texto):
        page.show_dialog(
            ft.SnackBar(content=ft.Text(texto))
        )

    nome_cliente = ft.TextField(
        label="Nome do cliente",
        value=comanda["cliente"] if editando else "",
        disabled=editando,
        border=ft.OutlineInputBorder(
            border_radius=12,
            side=ft.BorderSide(
                color=C.BORDER,
                width=1,
            ),
        ),
    )

    texto_total = ft.Text(
        "R$ 0,00",
        size=26,
        weight=ft.FontWeight.BOLD,
        color=C.PRIMARY,
    )

    def formatar_moeda(valor):
        return (
            f"R$ {valor:,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    def atualizar_total():
        total = sum(
            produto["preco"] * quantidades[produto["id"]]
            for produto in cardapio
        )
        texto_total.value = formatar_moeda(total)
        page.update()

    def alterar_quantidade(produto_id, diferenca):
        quantidades[produto_id] = max(
            0,
            quantidades[produto_id] + diferenca,
        )

        textos_quantidade[produto_id].value = str(
            quantidades[produto_id]
        )

        atualizar_total()

    def criar_linha_produto(produto):
        produto_id = produto["id"]

        texto_quantidade = ft.Text(
            "0",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=C.TEXT,
            width=28,
            text_align=ft.TextAlign.CENTER,
        )

        textos_quantidade[produto_id] = texto_quantidade

        return ft.Container(
            bgcolor=C.SURFACE,
            border_radius=12,
            padding=12,
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                produto["nome"],
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=C.TEXT,
                            ),
                            ft.Text(
                                formatar_moeda(produto["preco"]),
                                size=13,
                                color=C.TEXT_SECONDARY,
                            ),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.REMOVE,
                        icon_color=C.TEXT,
                        on_click=lambda e, pid=produto_id:
                            alterar_quantidade(pid, -1),
                    ),
                    texto_quantidade,
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_color=C.PRIMARY,
                        on_click=lambda e, pid=produto_id:
                            alterar_quantidade(pid, 1),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

    def confirmar(e):
        nonlocal salvando

        if salvando:
            return

        nome = (nome_cliente.value or "").strip()

        if not nome:
            mostrar_erro("Informe o nome do cliente.")
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
            print(f"Erro ao salvar itens: {erro}")

            mostrar_erro(
                "Não foi possível salvar os produtos. "
                "Verifique o terminal."
            )

            salvando = False
            botao_confirmar.disabled = False
            page.update()

    linhas_produtos = [
        criar_linha_produto(produto)
        for produto in cardapio
    ]

    if not linhas_produtos:
        linhas_produtos = [
            ft.Text(
                "Nenhum produto disponível.",
                color=C.TEXT_SECONDARY,
            )
        ]

    cabecalho = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=C.TEXT,
                on_click=lambda e: voltar(),
            ),
            ft.Text(
                "Adicionar itens" if editando
                else "Nova Comanda",
                size=22,
                weight=ft.FontWeight.BOLD,
                color=C.TEXT,
                expand=True,
            ),
        ],
    )

    resumo = ft.Container(
        bgcolor=C.SURFACE,
        border_radius=14,
        padding=16,
        content=ft.Row(
            controls=[
                ft.Text(
                    "Total selecionado",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=C.TEXT,
                ),
                texto_total,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
    )

    botao_confirmar = ft.Button(
        content=(
            "Adicionar produtos"
            if editando
            else "Criar comanda"
        ),
        bgcolor=C.PRIMARY,
        color=C.BACKGROUND,
        height=54,
        width=float("inf"),
        on_click=confirmar,
    )

    conteudo = ft.Column(
        controls=[
            cabecalho,
            nome_cliente,
            ft.Text(
                "Selecione os produtos",
                size=18,
                weight=ft.FontWeight.BOLD,
                color=C.TEXT,
            ),
            *linhas_produtos,
            resumo,
            botao_confirmar,
        ],
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

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

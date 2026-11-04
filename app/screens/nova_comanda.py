
import flet as ft

from app.theme.colors import AppColors as C
from app.data.comandas import (
    CARDAPIO,
    criar_comanda,
    adicionar_produtos,
    formatar_moeda,
)


def nova_comanda_screen(page, voltar, salvar, comanda=None):
    editando = comanda is not None
    quantidades = {p["nome"]: 0 for p in CARDAPIO}

    nome = ft.TextField(
        label="Nome do cliente",
        hint_text="Ex.: Carlos",
        value=comanda["cliente"] if editando else "",
        disabled=editando,
        bgcolor=C.SURFACE,
    )

    total_texto = ft.Text(
        "R$ 0,00",
        size=25,
        weight=ft.FontWeight.BOLD,
        color=C.PRIMARY,
    )

    def atualizar_total():
        total = sum(
            p["preco"] * quantidades[p["nome"]]
            for p in CARDAPIO
        )
        total_texto.value = formatar_moeda(total)
        total_texto.update()

    def criar_linha(produto):
        quantidade_texto = ft.Text(
            "0", size=17, width=30,
            text_align=ft.TextAlign.CENTER,
        )

        def alterar(valor):
            atual = quantidades[produto["nome"]]
            quantidades[produto["nome"]] = max(0, atual + valor)
            quantidade_texto.value = str(quantidades[produto["nome"]])
            quantidade_texto.update()
            atualizar_total()

        return ft.Container(
            bgcolor=C.SURFACE,
            border_radius=12,
            padding=12,
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                produto["nome"],
                                weight=ft.FontWeight.BOLD,
                                color=C.TEXT,
                            ),
                            ft.Text(
                                formatar_moeda(produto["preco"]),
                                color=C.PRIMARY,
                            ),
                        ],
                        expand=True,
                        spacing=5,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.REMOVE,
                        icon_color=C.TEXT,
                        on_click=lambda e: alterar(-1),
                    ),
                    quantidade_texto,
                    ft.IconButton(
                        icon=ft.Icons.ADD,
                        icon_color=C.PRIMARY,
                        on_click=lambda e: alterar(1),
                    ),
                ],
            ),
        )

    def mensagem(texto):
        page.show_dialog(
            ft.SnackBar(content=ft.Text(texto))
        )

    def confirmar(e):
        produtos = [
            {
                "nome": p["nome"],
                "preco": p["preco"],
                "quantidade": quantidades[p["nome"]],
            }
            for p in CARDAPIO
            if quantidades[p["nome"]] > 0
        ]

        try:
            if editando:
                adicionar_produtos(comanda, produtos)
                resultado = comanda
            else:
                resultado = criar_comanda(nome.value or "", produtos)

            salvar(resultado)
        except ValueError as erro:
            mensagem(str(erro))

    page.clean()
    page.navigation_bar = None
    page.bgcolor = C.BACKGROUND
    page.padding = 16

    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                icon_color=C.TEXT,
                                on_click=lambda e: voltar(),
                            ),
                            ft.Text(
                                "Adicionar itens" if editando else "Nova Comanda",
                                size=21,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ]
                    ),
                    nome,
                    ft.Text(
                        "Selecione os produtos",
                        size=19,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Column(
                        [criar_linha(p) for p in CARDAPIO],
                        spacing=10,
                        scroll=ft.ScrollMode.AUTO,
                        expand=True,
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                "Total dos novos itens",
                                weight=ft.FontWeight.BOLD,
                            ),
                            total_texto,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Button(
                        content="Adicionar itens" if editando else "Salvar Comanda",
                        bgcolor=C.PRIMARY,
                        color=C.BACKGROUND,
                        height=54,
                        width=float("inf"),
                        on_click=confirmar,
                    ),
                ],
                expand=True,
                spacing=14,
            ),
        )
    )


import flet as ft

from decimal import Decimal

from app.theme.colors import AppColors as C
from app.services.admin_produtos_service import (
    listar_todos_produtos_bd,
    cadastrar_produto_bd,
    atualizar_produto_bd,
    alterar_disponibilidade_bd,
)


def formatar_moeda(valor):
    numero = Decimal(str(valor))

    return (
        f"R$ {numero:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def gerenciar_cardapio_screen(
    page,
    voltar,
    cliente_supabase,
):
    produtos = []
    lista = ft.Column(spacing=12)

    def mensagem(texto):
        page.show_dialog(
            ft.SnackBar(content=ft.Text(texto))
        )

    def carregar_produtos():
        nonlocal produtos

        try:
            produtos = listar_todos_produtos_bd(
                cliente_supabase
            )
            atualizar_lista()

        except Exception as erro:
            print(f"Erro ao carregar cardápio: {erro}")
            mensagem("Não foi possível carregar o cardápio.")

    def abrir_formulario(produto=None):
        editando = produto is not None

        campo_nome = ft.TextField(
            label="Nome do produto",
            value=produto["nome"] if editando else "",
        )

        campo_categoria = ft.Dropdown(
            label="Categoria",
            value=produto["categoria"] if editando else "pastel",
            options=[
                ft.dropdown.Option("pastel", "Pastel"),
                ft.dropdown.Option("bebida", "Bebida"),
                ft.dropdown.Option("extra", "Extra"),
            ],
        )

        campo_preco = ft.TextField(
            label="Preço (R$)",
            value=(
                str(produto["preco"]).replace(".", ",")
                if editando else ""
            ),
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        def salvar(e):
            try:
                preco = (
                    (campo_preco.value or "")
                    .strip()
                    .replace(",", ".")
                )

                if editando:
                    atualizar_produto_bd(
                        cliente_supabase,
                        produto["id"],
                        campo_nome.value,
                        campo_categoria.value,
                        preco,
                    )
                else:
                    cadastrar_produto_bd(
                        cliente_supabase,
                        campo_nome.value,
                        campo_categoria.value,
                        preco,
                    )

                page.pop_dialog()
                carregar_produtos()
                mensagem("Produto salvo com sucesso!")

            except Exception as erro:
                mensagem(str(erro))

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Editar produto" if editando
                else "Novo produto"
            ),
            content=ft.Column(
                controls=[
                    campo_nome,
                    campo_categoria,
                    campo_preco,
                ],
                tight=True,
                spacing=12,
            ),
            actions=[
                ft.TextButton(
                    content="Cancelar",
                    on_click=lambda e: page.pop_dialog(),
                ),
                ft.Button(
                    content="Salvar",
                    bgcolor=C.PRIMARY,
                    color=C.BACKGROUND,
                    on_click=salvar,
                ),
            ],
        )

        page.show_dialog(dialogo)

    def mudar_disponibilidade(produto):
        try:
            nova_disponibilidade = not produto["disponivel"]

            alterar_disponibilidade_bd(
                cliente_supabase,
                produto["id"],
                nova_disponibilidade,
            )

            carregar_produtos()

        except Exception as erro:
            mensagem(str(erro))

    def criar_card(produto):
        disponivel = produto["disponivel"]

        return ft.Container(
            bgcolor=C.SURFACE,
            border_radius=14,
            border=ft.Border.all(1, C.BORDER),
            padding=14,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        produto["nome"],
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=C.TEXT,
                                    ),
                                    ft.Text(
                                        produto["categoria"].capitalize(),
                                        size=12,
                                        color=C.TEXT_SECONDARY,
                                    ),
                                ],
                                expand=True,
                                spacing=4,
                            ),
                            ft.Text(
                                formatar_moeda(produto["preco"]),
                                color=C.PRIMARY,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                    ft.Divider(color=C.BORDER),
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Disponível" if disponivel
                                else "Indisponível",
                                color=C.GREEN if disponivel
                                else C.RED,
                                size=12,
                            ),
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_OUTLINED,
                                        icon_color=C.PRIMARY,
                                        on_click=lambda e, p=produto:
                                            abrir_formulario(p),
                                    ),
                                    ft.Switch(
                                        value=disponivel,
                                        active_color=C.PRIMARY,
                                        on_change=lambda e, p=produto:
                                            mudar_disponibilidade(p),
                                    ),
                                ],
                                spacing=4,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=8,
            ),
        )

    def atualizar_lista(texto=""):
        lista.controls.clear()

        busca = (texto or "").strip().lower()

        filtrados = [
            produto
            for produto in produtos
            if busca in produto["nome"].lower()
            or busca in produto["categoria"].lower()
        ]

        if not filtrados:
            lista.controls.append(
                ft.Text(
                    "Nenhum produto encontrado.",
                    color=C.TEXT_SECONDARY,
                )
            )
        else:
            for produto in filtrados:
                lista.controls.append(criar_card(produto))

        if lista.page is not None:
            lista.update()

    pesquisa = ft.TextField(
        hint_text="Buscar produto...",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=C.SURFACE,
        on_change=lambda e:
            atualizar_lista(e.control.value),
    )

    cabecalho = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=C.TEXT,
                on_click=lambda e: voltar(),
            ),
            ft.Text(
                "Gerenciar Cardápio",
                size=20,
                weight=ft.FontWeight.BOLD,
                expand=True,
            ),
            ft.IconButton(
                icon=ft.Icons.ADD_CIRCLE,
                icon_color=C.PRIMARY,
                on_click=lambda e: abrir_formulario(),
            ),
        ],
    )

    page.clean()
    page.navigation_bar = None
    page.bgcolor = C.BACKGROUND
    page.padding = 16

    page.add(
        ft.SafeArea(
            content=ft.Column(
                controls=[
                    cabecalho,
                    pesquisa,
                    ft.Column(
                        controls=[lista],
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                expand=True,
                spacing=12,
            ),
            expand=True,
        )
    )

    carregar_produtos()


import flet as ft
from datetime import datetime

from app.theme.colors import AppColors as C
from app.data.comandas import (
    calcular_total,
    formatar_moeda,
    fechar_comanda,
)


def detalhes_comanda_screen(
    page,
    comanda,
    voltar,
    atualizar,
    adicionar_itens,
):
    fechada = comanda["status"] == "fechada"

    def criar_item(item):
        subtotal = item["quantidade"] * item["preco"]

        return ft.Container(
            padding=ft.Padding.symmetric(vertical=10),
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                item["nome"],
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=C.TEXT,
                            ),
                            ft.Text(
                                f'{item["quantidade"]} x '
                                f'{formatar_moeda(item["preco"])}',
                                size=13,
                                color=C.TEXT_SECONDARY,
                            ),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    ft.Text(
                        formatar_moeda(subtotal),
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=C.TEXT,
                    ),
                ],
            ),
        )

    def confirmar_fechamento(e):
        if comanda["status"] != "aberta":
            return

        fechar_comanda(comanda)

        page.pop_dialog()
        atualizar()

        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(
                    "Comanda fechada com sucesso!"
                )
            )
        )

    def solicitar_fechamento(e):
        if comanda["status"] != "aberta":
            return

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Fechar comanda?"),
                content=ft.Text(
                    f'Confirma o fechamento da comanda de '
                    f'{comanda["cliente"]} no valor de '
                    f'{formatar_moeda(calcular_total(comanda))}?'
                ),
                actions=[
                    ft.TextButton(
                        content="Cancelar",
                        on_click=lambda e: page.pop_dialog(),
                    ),
                    ft.TextButton(
                        content="Confirmar",
                        on_click=confirmar_fechamento,
                    ),
                ],
            )
        )

    itens = [
        criar_item(item)
        for item in comanda["produtos"]
    ]

    total = calcular_total(comanda)

    # Identifica a data de fechamento
    fechamento = comanda.get("fechada_em")

    if fechamento:
        data_fechamento = datetime.fromisoformat(fechamento)
        texto_fechamento = data_fechamento.strftime(
            "%d/%m/%Y às %H:%M"
        )
    else:
        texto_fechamento = None

    # Cabeçalho
    cabecalho = ft.Row(
        [
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=C.TEXT,
                on_click=lambda e: voltar(),
            ),
            ft.Text(
                f'Comanda #{comanda["id"]:02d}',
                size=21,
                weight=ft.FontWeight.BOLD,
                expand=True,
            ),
        ]
    )

    # Informações da comanda
    informacoes = [
        ft.Text(
            comanda["cliente"],
            size=23,
            weight=ft.FontWeight.BOLD,
            color=C.TEXT,
        ),
        ft.Text(
            "Finalizada" if fechada else "Em aberto",
            color=C.GREEN if fechada else C.PRIMARY,
            weight=ft.FontWeight.BOLD,
        ),
        ft.Text(
            f'Abertura: {comanda["horario"]}',
            color=C.TEXT_SECONDARY,
        ),
    ]

    if texto_fechamento:
        informacoes.append(
            ft.Text(
                f"Fechamento: {texto_fechamento}",
                color=C.TEXT_SECONDARY,
                size=13,
            )
        )

    informacoes.extend(
        [
            ft.Divider(color=C.BORDER),
            *itens,
            ft.Divider(color=C.BORDER),
            ft.Row(
                [
                    ft.Text(
                        "Total",
                        size=19,
                        weight=ft.FontWeight.BOLD,
                        color=C.TEXT,
                    ),
                    ft.Text(
                        formatar_moeda(total),
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=C.PRIMARY,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ]
    )

    # Cartão principal
    cartao = ft.Container(
        bgcolor=C.SURFACE,
        border_radius=14,
        padding=16,
        content=ft.Column(
            informacoes,
            spacing=12,
        ),
    )

    # Botões de ação
    botoes = ft.Column(
        [
            ft.Button(
                content="Adicionar mais itens",
                bgcolor=C.PRIMARY,
                color=C.BACKGROUND,
                height=54,
                width=float("inf"),
                visible=not fechada,
                on_click=lambda e: adicionar_itens(),
            ),
            ft.OutlinedButton(
                content="Fechar comanda",
                height=54,
                width=float("inf"),
                visible=not fechada,
                on_click=solicitar_fechamento,
            ),
        ],
        spacing=12,
    )

    # Estrutura da tela
    conteudo = ft.Column(
        [
            cabecalho,
            cartao,
            botoes,
        ],
        spacing=16,
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

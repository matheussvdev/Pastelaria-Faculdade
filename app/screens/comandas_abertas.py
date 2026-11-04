
import flet as ft

from app.theme.colors import AppColors as C
from app.data.comandas import COMANDAS, calcular_total, formatar_moeda


def comandas_abertas_screen(page: ft.Page, voltar, abrir_detalhes, abrir_nova):

    lista = ft.Column(spacing=12)

    def mensagem(texto):
        page.show_dialog(
            ft.SnackBar(content=ft.Text(texto))
        )

    def criar_card(comanda):
        quantidade = sum(
            item["quantidade"] for item in comanda["produtos"]
        )

        return ft.Container(
            bgcolor=C.SURFACE,
            border=ft.Border.all(1, C.BORDER),
            border_radius=14,
            padding=14,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                bgcolor=C.RED,
                                border_radius=10,
                                width=48,
                                height=48,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Text(
                                    str(comanda["id"]).zfill(2),
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=C.TEXT,
                                ),
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        comanda["cliente"],
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        comanda["horario"],
                                        size=12,
                                        color=C.TEXT_SECONDARY,
                                    ),
                                    ft.Text(
                                        f"{quantidade} itens | "
                                        f"{formatar_moeda(calcular_total(comanda))}",
                                        size=12,
                                        color=C.TEXT_SECONDARY,
                                    ),
                                ],
                                spacing=3,
                                expand=True,
                            ),
                            ft.Icon(
                                ft.Icons.CHEVRON_RIGHT,
                                color=C.TEXT,
                            ),
                        ]
                    ),
                    ft.Button(
                        content="Ver detalhes",
                        bgcolor=C.PRIMARY,
                        color=C.BACKGROUND,
                        width=float("inf"),
                        on_click=lambda e: abrir_detalhes(comanda),
                    ),
                ],
                spacing=12,
            ),
        )

    def atualizar_lista(texto=""):
        lista.controls.clear()

        filtradas = [
            c for c in COMANDAS
            if c["status"] == "aberta"
            and (
                texto.lower() in c["cliente"].lower()
                or texto in str(c["id"])
            )
        ]

        if not filtradas:
            lista.controls.append(
                ft.Text(
                    "Nenhuma comanda encontrada.",
                    color=C.TEXT_SECONDARY,
                )
            )
        else:
            for comanda in filtradas:
                lista.controls.append(criar_card(comanda))

        lista.update()

    pesquisa = ft.TextField(
        hint_text="Buscar comanda ou cliente...",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=C.SURFACE,
        border=ft.OutlineInputBorder(
            border_radius=12,
            side=ft.BorderSide(
                color=C.BORDER,
                width=1,
            ),
        ),
        on_change=lambda e: atualizar_lista(e.control.value),
    )

    cabecalho = ft.Row(
        [
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=C.TEXT,
                on_click=lambda e: voltar(),
            ),
            ft.Text(
                "Comandas Abertas",
                size=20,
                weight=ft.FontWeight.BOLD,
                expand=True,
            ),
            ft.Container(
                bgcolor=C.RED,
                border_radius=20,
                padding=8,
                content=ft.Text(
                    str(
                        sum(
                            1 for c in COMANDAS
                            if c["status"] == "aberta"
                        )
                    ),
                    color=C.TEXT,
                ),
            ),
        ]
    )

    page.clean()
    page.bgcolor = C.BACKGROUND
    page.padding = 16
    page.navigation_bar = None

    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Column(
                [
                    cabecalho,
                    pesquisa,
                    ft.Container(height=8),
                    ft.Column(
                        [lista],
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    ft.Button(
                        content="+ Nova Comanda",
                        bgcolor=C.PRIMARY,
                        color=C.BACKGROUND,
                        height=52,
                        width=float("inf"),
                       on_click=lambda e: abrir_nova(),
                    ),
                ],
                expand=True,
                spacing=12,
            ),
        )
    )

    atualizar_lista()

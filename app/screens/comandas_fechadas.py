
import flet as ft
from datetime import datetime

from app.theme.colors import AppColors as C
from app.data.comandas import (
    COMANDAS,
    calcular_total,
    formatar_moeda,
)


def comandas_fechadas_screen(page, voltar, abrir_detalhes):

    lista = ft.Column(spacing=12)

    def criar_card(comanda):
        quantidade = sum(
            item["quantidade"]
            for item in comanda["produtos"]
        )

        fechamento = comanda.get("fechada_em")

        if fechamento:
            data = datetime.fromisoformat(fechamento)
            horario = data.strftime("%d/%m/%Y às %H:%M")
        else:
            horario = "Horário não registrado"

        return ft.Container(
            bgcolor=C.SURFACE,
            border_radius=14,
            border=ft.Border.all(1, C.BORDER),
            padding=14,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                width=48,
                                height=48,
                                border_radius=12,
                                bgcolor="#193424",
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(
                                    ft.Icons.CHECK_CIRCLE,
                                    color=C.GREEN,
                                    size=28,
                                ),
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        comanda["cliente"],
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=C.TEXT,
                                    ),
                                    ft.Text(
                                        f'Comanda #{comanda["id"]:02d}',
                                        size=12,
                                        color=C.TEXT_SECONDARY,
                                    ),
                                    ft.Text(
                                        horario,
                                        size=12,
                                        color=C.TEXT_SECONDARY,
                                    ),
                                ],
                                expand=True,
                                spacing=4,
                            ),
                            ft.Text(
                                formatar_moeda(
                                    calcular_total(comanda)
                                ),
                                color=C.PRIMARY,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                    ft.Divider(color=C.BORDER),
                    ft.Row(
                        [
                            ft.Text(
                                f"{quantidade} itens · Finalizada",
                                color=C.GREEN,
                                size=12,
                            ),
                            ft.TextButton(
                                content="Ver detalhes",
                                on_click=lambda e: abrir_detalhes(
                                    comanda
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=10,
            ),
        )

    def atualizar_lista(texto=""):
        lista.controls.clear()

        filtradas = [
            c for c in COMANDAS
            if c["status"] == "fechada"
            and (
                texto.lower() in c["cliente"].lower()
                or texto in str(c["id"])
            )
        ]

        filtradas.sort(
            key=lambda c: c.get("fechada_em", ""),
            reverse=True,
        )

        if not filtradas:
            lista.controls.append(
                ft.Container(
                    padding=30,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.RECEIPT_LONG,
                                size=48,
                                color=C.TEXT_SECONDARY,
                            ),
                            ft.Text(
                                "Nenhuma comanda fechada encontrada.",
                                color=C.TEXT_SECONDARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                )
            )
        else:
            for comanda in filtradas:
                lista.controls.append(criar_card(comanda))

        lista.update()

    pesquisa = ft.TextField(
        hint_text="Buscar cliente ou comanda...",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=C.SURFACE,
        border=ft.OutlineInputBorder(
            border_radius=12,
            side=ft.BorderSide(
                color=C.BORDER,
                width=1,
            ),
        ),
        on_change=lambda e: atualizar_lista(
            e.control.value or ""
        ),
    )

    total_fechadas = sum(
        1 for c in COMANDAS
        if c["status"] == "fechada"
    )

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
                                "Comandas Fechadas",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                expand=True,
                            ),
                            ft.Container(
                                bgcolor="#193424",
                                border_radius=20,
                                padding=8,
                                content=ft.Text(
                                    str(total_fechadas),
                                    color=C.GREEN,
                                ),
                            ),
                        ]
                    ),
                    pesquisa,
                    ft.Column(
                        [lista],
                        expand=True,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                expand=True,
                spacing=12,
            ),
        )
    )

    atualizar_lista()

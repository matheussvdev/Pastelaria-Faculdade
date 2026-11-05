
import flet as ft

from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.theme.colors import AppColors as C
from app.services.comandas_service import (
    listar_comandas_fechadas_bd,
    buscar_detalhes_comanda_bd,
)


def formatar_moeda(valor):
    numero = Decimal(str(valor))

    return (
        f"R$ {numero:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def formatar_data(data_iso):
    if not data_iso:
        return "Horário não registrado"

    try:
        data = datetime.fromisoformat(
            data_iso.replace("Z", "+00:00")
        )

        data = data.astimezone(
            ZoneInfo("America/Sao_Paulo")
        )

        return data.strftime("%d/%m/%Y às %H:%M")

    except (ValueError, TypeError):
        return "Horário não registrado"


def comandas_fechadas_screen(
    page,
    voltar,
    abrir_detalhes,
    cliente_supabase,
):
    lista = ft.Column(spacing=12)

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
            comandas.append(detalhes)

    except Exception as erro:
        print(f"Erro ao carregar comandas fechadas: {erro}")

        comandas = []

        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(
                    "Não foi possível carregar as comandas fechadas."
                )
            )
        )

    def criar_card(comanda):
        quantidade = sum(
            item["quantidade"]
            for item in comanda["itens"]
        )

        horario = formatar_data(
            comanda.get("fechada_em")
        )

        return ft.Container(
            bgcolor=C.SURFACE,
            border_radius=14,
            border=ft.Border.all(1, C.BORDER),
            padding=14,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
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
                                controls=[
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
                                    comanda["total"]
                                ),
                                color=C.PRIMARY,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                    ft.Divider(color=C.BORDER),
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"{quantidade} itens · Finalizada",
                                color=C.GREEN,
                                size=12,
                            ),
                            ft.TextButton(
                                content="Ver detalhes",
                                on_click=lambda e, c=comanda:
                                    abrir_detalhes(c),
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

        texto = (texto or "").strip().lower()

        filtradas = [
            comanda
            for comanda in comandas
            if (
                texto in comanda["cliente"].lower()
                or texto in str(comanda["id"])
            )
        ]

        if not filtradas:
            lista.controls.append(
                ft.Container(
                    padding=30,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        controls=[
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
                lista.controls.append(
                    criar_card(comanda)
                )

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
        on_change=lambda e:
            atualizar_lista(e.control.value or ""),
    )

    total_fechadas = len(comandas)

    cabecalho = ft.Row(
        controls=[
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
    )

    page.clean()
    page.navigation_bar = None
    page.bgcolor = C.BACKGROUND
    page.padding = 16

    page.add(
        ft.SafeArea(
            expand=True,
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
        )
    )

    atualizar_lista()


import flet as ft
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.theme.colors import AppColors as C
from app.services.comandas_service import (
    listar_comandas_abertas_bd,
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


def formatar_horario(data_iso):
    if not data_iso:
        return "Horário indisponível"

    try:
        data = datetime.fromisoformat(
            data_iso.replace("Z", "+00:00")
        )
        data = data.astimezone(
            ZoneInfo("America/Sao_Paulo")
        )
        return data.strftime("%d/%m/%Y às %H:%M")
    except (ValueError, TypeError):
        return "Horário indisponível"


def comandas_abertas_screen(
    page: ft.Page,
    voltar,
    abrir_detalhes,
    abrir_nova,
    cliente_supabase,
):
    lista = ft.Column(spacing=12)

    def mensagem(texto):
        page.show_dialog(
            ft.SnackBar(content=ft.Text(texto))
        )

    try:
        registros = listar_comandas_abertas_bd(
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
        print(f"Erro ao carregar comandas: {erro}")
        mensagem(
            "Não foi possível carregar as comandas."
        )
        comandas = []

    def criar_card(comanda):
        quantidade = sum(
            item["quantidade"]
            for item in comanda["itens"]
        )

        return ft.Container(
            bgcolor=C.SURFACE,
            border=ft.Border.all(1, C.BORDER),
            border_radius=14,
            padding=14,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
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
                                controls=[
                                    ft.Text(
                                        comanda["cliente"],
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=C.TEXT,
                                    ),
                                    ft.Text(
                                        formatar_horario(
                                            comanda["aberta_em"]
                                        ),
                                        size=12,
                                        color=C.TEXT_SECONDARY,
                                    ),
                                    ft.Text(
                                        f"{quantidade} itens | "
                                        f"{formatar_moeda(comanda['total'])}",
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
                        on_click=lambda e, c=comanda:
                            abrir_detalhes(c),
                    ),
                ],
                spacing=12,
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
                ft.Text(
                    "Nenhuma comanda encontrada.",
                    color=C.TEXT_SECONDARY,
                )
            )
        else:
            for comanda in filtradas:
                lista.controls.append(
                    criar_card(comanda)
                )

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
                    str(len(comandas)),
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
                controls=[
                    cabecalho,
                    pesquisa,
                    ft.Container(height=8),
                    ft.Column(
                        controls=[lista],
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

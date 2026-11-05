
import flet as ft

from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.theme.colors import AppColors as C
from app.services.comandas_service import fechar_comanda_bd


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
        return "Data indisponível"

    try:
        data = datetime.fromisoformat(
            data_iso.replace("Z", "+00:00")
        )

        data = data.astimezone(
            ZoneInfo("America/Sao_Paulo")
        )

        return data.strftime("%d/%m/%Y às %H:%M")

    except (ValueError, TypeError):
        return "Data indisponível"


def detalhes_comanda_screen(
    page,
    comanda,
    voltar,
    atualizar,
    adicionar_itens,
    cliente_supabase,
):
    fechada = comanda["status"] == "fechada"

    def mostrar_mensagem(texto):
        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(texto)
            )
        )

    def criar_item(item):
        quantidade = item["quantidade"]
        preco = item["preco_unitario"]
        subtotal = item["subtotal"]

        return ft.Container(
            padding=ft.Padding.symmetric(vertical=10),
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                item["nome"],
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=C.TEXT,
                            ),
                            ft.Text(
                                f"{quantidade} x "
                                f"{formatar_moeda(preco)}",
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

        try:
            total_fechado = fechar_comanda_bd(
                cliente_supabase,
                int(comanda["id"]),
            )

        except Exception as erro:
            print(f"Erro ao fechar comanda: {erro}")
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
            f"Comanda fechada com sucesso! "
            f"Total: {formatar_moeda(total_fechado)}"
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
                    f'{formatar_moeda(comanda["total"])}?'
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
        for item in comanda["itens"]
    ]

    if not itens:
        itens = [
            ft.Text(
                "Esta comanda não possui itens.",
                color=C.TEXT_SECONDARY,
            )
        ]

    texto_abertura = formatar_data(
        comanda.get("aberta_em")
    )

    fechamento = comanda.get("fechada_em")

    texto_fechamento = (
        formatar_data(fechamento)
        if fechamento
        else None
    )

    cabecalho = ft.Row(
        controls=[
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
        ],
    )

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
            f"Abertura: {texto_abertura}",
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
                controls=[
                    ft.Text(
                        "Total",
                        size=19,
                        weight=ft.FontWeight.BOLD,
                        color=C.TEXT,
                    ),
                    ft.Text(
                        formatar_moeda(comanda["total"]),
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=C.PRIMARY,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ]
    )

    cartao = ft.Container(
        bgcolor=C.SURFACE,
        border_radius=14,
        padding=16,
        content=ft.Column(
            controls=informacoes,
            spacing=12,
        ),
    )

    botoes = ft.Column(
        controls=[
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
            ft.Text(
                "A adição de itens será habilitada "
                "na próxima etapa.",
                size=12,
                color=C.TEXT_SECONDARY,
                visible=not fechada,
                text_align=ft.TextAlign.CENTER,
            ),
        ],
        spacing=12,
    )

    conteudo = ft.Column(
        controls=[
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

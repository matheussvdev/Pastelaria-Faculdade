
import flet as ft
from app.theme.colors import AppColors as C

def home_screen(page: ft.Page, abrir_comandas=None, abrir_fechadas=None):

    def mostrar_mensagem(texto):
        page.show_dialog(
            ft.SnackBar(content=ft.Text(texto))
        )

    def criar_atalho(titulo, icone, destaque=False, contador=None):
        cor_fundo = C.PRIMARY if destaque else C.SURFACE
        cor_texto = C.BACKGROUND if destaque else C.TEXT

        conteudo = [
            ft.Icon(icone, size=34, color=cor_texto),
            ft.Text(
                titulo,
                size=15,
                weight=ft.FontWeight.BOLD,
                color=cor_texto,
                text_align=ft.TextAlign.CENTER,
            ),
        ]

        if contador is not None:
            conteudo.append(
                ft.Text(
                    f"{contador} em aberto",
                    color=cor_texto,
                    size=12,
                )
            )

        return ft.Container(
            content=ft.Column(
                conteudo,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=cor_fundo,
            border_radius=14,
            padding=14,
            height=145,
            expand=True,
     on_click=lambda e: (
    abrir_comandas()
    if titulo.startswith("Comandas\nAbertas") and abrir_comandas
    else abrir_fechadas()
    if titulo.startswith("Comandas\nFechadas") and abrir_fechadas
    else mostrar_mensagem(titulo)
),
        )

    cabecalho = ft.Row(
        [
            ft.Icon(ft.Icons.MENU, color=C.TEXT),
            ft.Column(
                [
                    ft.Text(
                        "PASTELARIA",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=C.TEXT,
                    ),
                    ft.Text(
                        "SABOR EM CADA MORDIDA",
                        size=9,
                        color=C.PRIMARY,
                    ),
                ],
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Icon(ft.Icons.ACCOUNT_CIRCLE_OUTLINED, color=C.RED),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    atalhos = ft.Column(
        [
            ft.Row(
                [
                    criar_atalho(
                        "Comandas\nAbertas",
                        ft.Icons.RECEIPT_LONG,
                        destaque=True,
                        contador=3,
                    ),
                    criar_atalho(
                        "Comandas\nFechadas",
                        ft.Icons.CHECK_CIRCLE_OUTLINE,
                    ),
                ],
                spacing=12,
            ),
            ft.Row(
                [
                    criar_atalho(
                        "Novo Pedido",
                        ft.Icons.ADD_CIRCLE_OUTLINE,
                    ),
                    criar_atalho(
                        "Cardápio",
                        ft.Icons.RESTAURANT_MENU,
                    ),
                ],
                spacing=12,
            ),
        ],
        spacing=12,
    )

    navegacao = ft.NavigationBar(
        selected_index=0,
        bgcolor=C.BACKGROUND,
        indicator_color=C.SURFACE,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME_OUTLINED,
                selected_icon=ft.Icons.HOME,
                label="Início",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.RECEIPT_LONG_OUTLINED,
                selected_icon=ft.Icons.RECEIPT_LONG,
                label="Pedidos",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.MENU,
                label="Mais",
            ),
        ],
        on_change=lambda e: mostrar_mensagem(
            ["Início", "Pedidos", "Mais"][e.control.selected_index]
        ),
    )

    conteudo = ft.Column(
        [
            cabecalho,
            ft.Container(height=22),
            ft.Text(
                "Olá, atendente!",
                size=25,
                weight=ft.FontWeight.BOLD,
                color=C.TEXT,
            ),
            ft.Text(
                "Vamos deixar o dia ainda mais saboroso?",
                size=13,
                color=C.TEXT_SECONDARY,
            ),
            ft.Container(height=18),
            atalhos,
        ],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    page.clean()
    page.bgcolor = C.BACKGROUND
    page.padding = 16
    page.navigation_bar = navegacao
    page.add(
        ft.SafeArea(
            content=ft.Container(
                content=conteudo,
                alignment=ft.Alignment.TOP_CENTER,
                expand=True,
            ),
            expand=True,
        )
    )

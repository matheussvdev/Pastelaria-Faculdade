
import flet as ft

from app.theme.colors import AppColors as C


def login_screen(page, autenticar):
    email = ft.TextField(
        label="E-mail",
        keyboard_type=ft.KeyboardType.EMAIL,
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border=ft.OutlineInputBorder(
            border_radius=12,
            side=ft.BorderSide(color=C.BORDER, width=1),
        ),
    )

    senha = ft.TextField(
        label="Senha",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        border=ft.OutlineInputBorder(
            border_radius=12,
            side=ft.BorderSide(color=C.BORDER, width=1),
        ),
    )

    mensagem = ft.Text(
        "",
        color=C.RED,
        size=13,
        visible=False,
    )

    botao_entrar = ft.Button(
        content="Entrar",
        bgcolor=C.PRIMARY,
        color=C.BACKGROUND,
        height=54,
        width=float("inf"),
    )

    def entrar(e):
        mensagem.visible = False

        if not email.value or not senha.value:
            mensagem.value = "Informe seu e-mail e sua senha."
            mensagem.visible = True
            page.update()
            return

        botao_entrar.disabled = True
        page.update()

        try:
            autenticar(
                email.value.strip(),
                senha.value,
            )
        except Exception:
            mensagem.value = (
                "Não foi possível entrar. "
                "Verifique suas credenciais e tente novamente."
            )
            mensagem.visible = True
            botao_entrar.disabled = False
            page.update()

    botao_entrar.on_click = entrar

    conteudo = ft.Column(
        controls=[
            ft.Container(height=55),
            ft.Icon(
                ft.Icons.RESTAURANT_MENU,
                size=58,
                color=C.PRIMARY,
            ),
            ft.Text(
                "Pastelaria",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=C.TEXT,
            ),
            ft.Text(
                "Acesse sua conta para gerenciar os pedidos",
                color=C.TEXT_SECONDARY,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=28),
            email,
            senha,
            mensagem,
            ft.Container(height=12),
            botao_entrar,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    page.clean()
    page.navigation_bar = None
    page.bgcolor = C.BACKGROUND
    page.padding = 24

    page.add(
        ft.SafeArea(
            content=conteudo,
            expand=True,
        )
    )

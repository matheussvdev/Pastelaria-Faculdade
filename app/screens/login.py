
import flet as ft

from app.theme.colors import AppColors as C


def login_screen(page: ft.Page, autenticar, abrir_cadastro=None):
    AMARELO = C.PRIMARY
    FUNDO = C.BACKGROUND
    SUPERFICIE = C.SURFACE
    TEXTO = C.TEXT
    TEXTO_SECUNDARIO = C.TEXT_SECONDARY
    BORDA = C.BORDER

    def criar_borda(cor, largura=1):
        lado = ft.BorderSide(width=largura, color=cor)
        return ft.Border(
            left=lado,
            top=lado,
            right=lado,
            bottom=lado,
        )

    email = ft.TextField(
        label="E-mail",
        hint_text="Digite seu e-mail",
        keyboard_type=ft.KeyboardType.EMAIL,
        prefix_icon=ft.Icons.EMAIL_OUTLINED,
        border_color=BORDA,
        focused_border_color=AMARELO,
        border_radius=12,
        bgcolor=SUPERFICIE,
        text_size=15,
        height=60,
    )

    senha = ft.TextField(
        label="Senha",
        hint_text="Digite sua senha",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        border_color=BORDA,
        focused_border_color=AMARELO,
        border_radius=12,
        bgcolor=SUPERFICIE,
        text_size=15,
        height=60,
        on_submit=lambda e: entrar(e),
    )

    mensagem = ft.Text(
        "",
        color=C.RED,
        size=13,
        visible=False,
        text_align=ft.TextAlign.CENTER,
    )

    botao_entrar = ft.Button(
        content=ft.Row(
            controls=[
                ft.Text(
                    "Entrar",
                    weight=ft.FontWeight.BOLD,
                    size=16,
                ),
                ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, size=20),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        bgcolor=AMARELO,
        color=FUNDO,
        height=56,
        width=float("inf"),
    )

    def entrar(e):
        mensagem.visible = False

        email_informado = (email.value or "").strip()
        senha_informada = senha.value or ""

        if not email_informado or not senha_informada:
            mensagem.value = "Informe seu e-mail e sua senha."
            mensagem.visible = True
            page.update()
            return

        botao_entrar.disabled = True
        page.update()

        try:
            autenticar(email_informado, senha_informada)
        except Exception as erro:
            print(f"Erro no login: {erro}")
            mensagem.value = (
                "Não foi possível entrar. "
                "Verifique seu e-mail e sua senha."
            )
            mensagem.visible = True
            botao_entrar.disabled = False
            page.update()

    botao_entrar.on_click = entrar

    def cadastrar(e):
        if abrir_cadastro is not None:
            abrir_cadastro()

    botao_cadastro = ft.TextButton(
        content=ft.Text(
            "Criar conta de funcionário",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=AMARELO,
        ),
        on_click=cadastrar if abrir_cadastro is not None else None,
        disabled=abrir_cadastro is None,
    )

    logotipo = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    width=108,
                    height=108,
                    border_radius=54,
                    bgcolor=SUPERFICIE,
                    border=criar_borda(AMARELO, 2),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(
                        ft.Icons.BAKERY_DINING_ROUNDED,
                        size=66,
                        color=AMARELO,
                    ),
                ),
                ft.Text(
                    "PASTELARIA",
                    size=34,
                    weight=ft.FontWeight.BOLD,
                    color=TEXTO,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "SABOR EM CADA MORDIDA",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=AMARELO,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        alignment=ft.Alignment.CENTER,
    )

    formulario = ft.Container(
        bgcolor=SUPERFICIE,
        border_radius=20,
        border=criar_borda(BORDA),
        padding=22,
        content=ft.Column(
            controls=[
                ft.Text(
                    "Bem-vindo de volta!",
                    size=23,
                    weight=ft.FontWeight.BOLD,
                    color=TEXTO,
                ),
                ft.Text(
                    "Entre com suas credenciais para continuar.",
                    size=13,
                    color=TEXTO_SECUNDARIO,
                ),
                ft.Container(height=8),
                email,
                senha,
                mensagem,
                ft.Container(height=4),
                botao_entrar,
                ft.Divider(color=BORDA, height=24),
                ft.Text(
                    "Novo por aqui?",
                    size=13,
                    color=TEXTO_SECUNDARIO,
                    text_align=ft.TextAlign.CENTER,
                ),
                botao_cadastro,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=12,
        ),
    )

    conteudo = ft.Column(
        controls=[
            ft.Container(height=35),
            logotipo,
            ft.Container(height=25),
            formulario,
            ft.Container(height=18),
            ft.Text(
                "Sistema de gerenciamento de comandas",
                size=12,
                color=TEXTO_SECUNDARIO,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                "Versão acadêmica • 1.0",
                size=11,
                color=TEXTO_SECUNDARIO,
                text_align=ft.TextAlign.CENTER,
            ),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
    )

    page.clean()
    page.navigation_bar = None
    page.drawer = None
    page.bgcolor = FUNDO
    page.padding = 20

    page.add(
        ft.SafeArea(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=conteudo,
                        width=420,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START,
                expand=True,
            ),
            expand=True,
        )
    )

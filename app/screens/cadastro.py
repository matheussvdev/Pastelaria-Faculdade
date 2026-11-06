
import re
import flet as ft

from app.theme.colors import AppColors as C


def cadastro_screen(page: ft.Page, cadastrar, voltar):

    def criar_borda(cor, largura=1):
        lado = ft.BorderSide(
            width=largura,
            color=cor,
        )

        return ft.Border(
            left=lado,
            top=lado,
            right=lado,
            bottom=lado,
        )

    def criar_campo(label, icone, senha=False):
        return ft.TextField(
            label=label,
            prefix_icon=icone,
            password=senha,
            can_reveal_password=senha,
            border_color=C.BORDER,
            focused_border_color=C.PRIMARY,
            border_radius=12,
            bgcolor=C.SURFACE,
            height=60,
            text_size=15,
        )

    # =========================================
    # CAMPOS
    # =========================================

    nome = criar_campo(
        "Nome completo",
        ft.Icons.PERSON_OUTLINE,
    )

    email = criar_campo(
        "E-mail",
        ft.Icons.EMAIL_OUTLINED,
    )
    email.keyboard_type = ft.KeyboardType.EMAIL

    senha = criar_campo(
        "Senha",
        ft.Icons.LOCK_OUTLINE,
        senha=True,
    )

    confirmar_senha = criar_campo(
        "Confirmar senha",
        ft.Icons.LOCK_RESET_OUTLINED,
        senha=True,
    )

    mensagem = ft.Text(
        "",
        color=C.RED,
        size=13,
        visible=False,
        text_align=ft.TextAlign.CENTER,
    )

    def mostrar_erro(texto):
        mensagem.value = texto
        mensagem.color = C.RED
        mensagem.visible = True
        page.update()

    def mostrar_sucesso(texto):
        mensagem.value = texto
        mensagem.color = "#4ADE80"
        mensagem.visible = True
        page.update()

    # =========================================
    # CADASTRAR
    # =========================================

    def registrar(e):
        mensagem.visible = False

        nome_informado = (nome.value or "").strip()
        email_informado = (email.value or "").strip()
        senha_informada = senha.value or ""
        confirmacao = confirmar_senha.value or ""

        if len(nome_informado) < 3:
            mostrar_erro(
                "Informe um nome com pelo menos 3 caracteres."
            )
            return

        if len(nome_informado) > 100:
            mostrar_erro(
                "O nome deve ter no máximo 100 caracteres."
            )
            return

        if not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email_informado,
        ):
            mostrar_erro("Informe um e-mail válido.")
            return

        if len(senha_informada) < 8:
            mostrar_erro(
                "A senha deve ter pelo menos 8 caracteres."
            )
            return

        if senha_informada != confirmacao:
            mostrar_erro("As senhas não coincidem.")
            return

        botao_cadastrar.disabled = True
        page.update()

        try:
            precisa_confirmar_email = cadastrar(
                nome_informado,
                email_informado,
                senha_informada,
            )

        except Exception as erro:
            print(
                "Erro ao cadastrar funcionário:",
                type(erro).__name__,
            )

            botao_cadastrar.disabled = False

            mostrar_erro(
                "Não foi possível criar a conta. "
                "Verifique os dados e tente novamente."
            )
            return

        # O cadastro foi aceito pelo Supabase.
        nome.disabled = True
        email.disabled = True
        senha.disabled = True
        confirmar_senha.disabled = True

        senha.value = ""
        confirmar_senha.value = ""

        botao_cadastrar.visible = False
        botao_voltar_login.visible = True

        if precisa_confirmar_email:
            mostrar_sucesso(
                "Solicitação de cadastro recebida! "
                "Verifique seu e-mail para confirmar a conta. "
                "Depois, volte ao login."
            )
        else:
            mostrar_sucesso(
                "Cadastro realizado com sucesso! "
                "Agora você pode entrar com sua nova conta."
            )

    # =========================================
    # BOTÕES
    # =========================================

    botao_cadastrar = ft.Button(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.PERSON_ADD_ALT_1),
                ft.Text(
                    "Criar conta",
                    weight=ft.FontWeight.BOLD,
                    size=16,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        bgcolor=C.PRIMARY,
        color=C.BACKGROUND,
        height=56,
        width=float("inf"),
        on_click=registrar,
    )

    botao_voltar_login = ft.Button(
        content="Ir para o login",
        bgcolor=C.PRIMARY,
        color=C.BACKGROUND,
        height=54,
        width=float("inf"),
        visible=False,
        on_click=lambda e: voltar(),
    )

    # =========================================
    # FORMULÁRIO
    # =========================================

    formulario = ft.Container(
        bgcolor=C.SURFACE,
        border_radius=20,
        border=criar_borda(C.BORDER),
        padding=22,
        content=ft.Column(
            controls=[
                ft.Text(
                    "Criar conta",
                    size=26,
                    weight=ft.FontWeight.BOLD,
                    color=C.TEXT,
                ),
                ft.Text(
                    "Cadastre-se para acessar o sistema da pastelaria.",
                    size=13,
                    color=C.TEXT_SECONDARY,
                ),
                ft.Container(height=10),
                nome,
                email,
                senha,
                confirmar_senha,
                mensagem,
                ft.Container(height=6),
                botao_cadastrar,
                botao_voltar_login,
                ft.Text(
                    "Novas contas possuem acesso de funcionário.",
                    size=12,
                    color=C.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.TextButton(
                    content=ft.Text(
                        "Já tenho uma conta. Entrar",
                        color=C.PRIMARY,
                    ),
                    on_click=lambda e: voltar(),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=12,
        ),
    )

    # =========================================
    # CONTEÚDO
    # =========================================

    conteudo = ft.Column(
        controls=[
            ft.Container(height=20),
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=C.TEXT,
                        on_click=lambda e: voltar(),
                    ),
                    ft.Text(
                        "Cadastro de funcionário",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=C.TEXT,
                    ),
                ],
            ),
            ft.Container(height=15),
            ft.Icon(
                ft.Icons.BAKERY_DINING_ROUNDED,
                size=65,
                color=C.PRIMARY,
            ),
            ft.Text(
                "PASTELARIA",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=C.TEXT,
            ),
            ft.Container(height=15),
            formulario,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
    )

    page.clean()
    page.navigation_bar = None
    page.drawer = None
    page.bgcolor = C.BACKGROUND
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

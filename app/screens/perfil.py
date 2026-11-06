
import flet as ft

from app.theme.colors import AppColors as C


def perfil_screen(
    page: ft.Page,
    usuario=None,
    voltar=None,
    sair=None,
    salvar_nome=None,
    salvar_foto=None,
    remover_foto=None,
    foto_bytes=None,
    alterar_senha=None,
):
    usuario = usuario or {}

    nome = usuario.get("nome") or "Usuário"
    email = usuario.get("email") or "Não informado"
    funcao = usuario.get("funcao", "atendente")
    administrador = funcao == "admin"

    nome_funcao = (
        "Administrador" if administrador else "Funcionário"
    )

    def mostrar_mensagem(texto):
        page.show_dialog(
            ft.SnackBar(content=ft.Text(texto))
        )

    def executar_voltar(e):
        if voltar is not None:
            voltar()

    def executar_sair(e):
        if sair is not None:
            sair()

    def atualizar_tela():
        perfil_screen(
            page,
            usuario=usuario,
            voltar=voltar,
            sair=sair,
            salvar_nome=salvar_nome,
            salvar_foto=salvar_foto,
            remover_foto=remover_foto,
            foto_bytes=usuario.get("_foto_bytes"),
            alterar_senha=alterar_senha,
        )

    # =========================================
    # EDITAR NOME
    # =========================================

    campo_nome = ft.TextField(
        label="Nome da conta",
        value=nome,
        border_color=C.PRIMARY,
        focused_border_color=C.PRIMARY,
        max_length=100,
    )

    def fechar_edicao(e=None):
        page.pop_dialog()

    def confirmar_nome(e):
        novo_nome = (campo_nome.value or "").strip()

        if not 3 <= len(novo_nome) <= 100:
            mostrar_mensagem(
                "O nome deve ter entre 3 e 100 caracteres."
            )
            return

        if salvar_nome is None:
            mostrar_mensagem(
                "A edição do nome não está disponível."
            )
            return

        try:
            salvar_nome(novo_nome)
        except Exception as erro:
            print(f"Erro ao atualizar nome: {erro}")
            mostrar_mensagem(
                "Não foi possível atualizar o nome."
            )
            return

        fechar_edicao()
        atualizar_tela()
        mostrar_mensagem("Nome atualizado com sucesso!")

    def abrir_edicao(e):
        campo_nome.value = usuario.get("nome") or ""

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Editar nome"),
                content=campo_nome,
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=fechar_edicao,
                    ),
                    ft.TextButton(
                        "Salvar",
                        on_click=confirmar_nome,
                    ),
                ],
            )
        )

    # =========================================
    # ALTERAR SENHA
    # =========================================

    campo_senha_atual = ft.TextField(
        label="Senha atual",
        password=True,
        can_reveal_password=True,
        border_color=C.PRIMARY,
        focused_border_color=C.PRIMARY,
    )

    campo_nova_senha = ft.TextField(
        label="Nova senha",
        password=True,
        can_reveal_password=True,
        border_color=C.PRIMARY,
        focused_border_color=C.PRIMARY,
    )

    campo_confirmar_senha = ft.TextField(
        label="Confirmar nova senha",
        password=True,
        can_reveal_password=True,
        border_color=C.PRIMARY,
        focused_border_color=C.PRIMARY,
    )

    def fechar_dialogo_senha(e=None):
        page.pop_dialog()

    def confirmar_alteracao_senha(e):
        senha_atual = campo_senha_atual.value or ""
        nova_senha = campo_nova_senha.value or ""
        confirmacao = campo_confirmar_senha.value or ""

        if not senha_atual or not nova_senha or not confirmacao:
            mostrar_mensagem("Preencha todos os campos.")
            return

        if len(nova_senha) < 8:
            mostrar_mensagem(
                "A nova senha deve ter pelo menos 8 caracteres."
            )
            return

        if nova_senha != confirmacao:
            mostrar_mensagem(
                "A confirmação não corresponde à nova senha."
            )
            return

        if nova_senha == senha_atual:
            mostrar_mensagem(
                "A nova senha deve ser diferente da atual."
            )
            return

        if alterar_senha is None:
            mostrar_mensagem(
                "A alteração de senha não está disponível."
            )
            return

        try:
            alterar_senha(senha_atual, nova_senha)

        except ValueError as erro:
            mostrar_mensagem(str(erro))
            return

        except Exception as erro:
            print(f"Erro ao alterar senha: {erro}")
            mostrar_mensagem(
                "Não foi possível alterar a senha. "
                "Verifique sua conexão e tente novamente."
            )
            return

        campo_senha_atual.value = ""
        campo_nova_senha.value = ""
        campo_confirmar_senha.value = ""

        fechar_dialogo_senha()
        mostrar_mensagem("Senha alterada com sucesso!")

    def abrir_alteracao_senha(e):
        campo_senha_atual.value = ""
        campo_nova_senha.value = ""
        campo_confirmar_senha.value = ""

        page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Alterar senha"),
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Informe sua senha atual e escolha "
                            "uma nova senha com pelo menos "
                            "8 caracteres.",
                            size=13,
                            color=C.TEXT_SECONDARY,
                        ),
                        campo_senha_atual,
                        campo_nova_senha,
                        campo_confirmar_senha,
                    ],
                    spacing=12,
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=fechar_dialogo_senha,
                    ),
                    ft.TextButton(
                        "Salvar senha",
                        on_click=confirmar_alteracao_senha,
                    ),
                ],
            )
        )

    # =========================================
    # FOTO DE PERFIL
    # =========================================

    seletor_foto = ft.FilePicker()
    page.services.append(seletor_foto)

    async def escolher_foto(e):
        if salvar_foto is None:
            mostrar_mensagem(
                "O envio de fotos não está disponível."
            )
            return

        try:
            arquivos = await seletor_foto.pick_files(
                dialog_title="Escolher foto de perfil",
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=[
                    "jpg", "jpeg", "png", "webp"
                ],
                allow_multiple=False,
                with_data=True,
            )

            if not arquivos:
                return

            arquivo = arquivos[0]

            if arquivo.size and arquivo.size > 2 * 1024 * 1024:
                mostrar_mensagem(
                    "A imagem deve ter no máximo 2 MB."
                )
                return

            dados = arquivo.bytes

            if dados is None:
                mostrar_mensagem(
                    "Não foi possível ler a imagem."
                )
                return

            salvar_foto(arquivo.name, dados)

            atualizar_tela()
            mostrar_mensagem(
                "Foto de perfil atualizada com sucesso!"
            )

        except Exception as erro:
            print(f"Erro ao selecionar foto: {erro}")
            mostrar_mensagem(
                f"Não foi possível atualizar a foto: {erro}"
            )

    def excluir_foto(e):
        if remover_foto is None:
            mostrar_mensagem(
                "A remoção de fotos não está disponível."
            )
            return

        try:
            remover_foto()
            atualizar_tela()
            mostrar_mensagem("Foto removida com sucesso!")

        except Exception as erro:
            print(f"Erro ao remover foto: {erro}")
            mostrar_mensagem(
                "Não foi possível remover a foto."
            )

    # =========================================
    # COMPONENTES
    # =========================================

    def campo_informacao(titulo, valor, icone, acao=None):
        controles = [
            ft.Icon(
                icone,
                color=C.PRIMARY,
                size=24,
            ),
            ft.Column(
                controls=[
                    ft.Text(
                        titulo,
                        size=12,
                        color=C.TEXT_SECONDARY,
                    ),
                    ft.Text(
                        valor,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=C.TEXT,
                        selectable=True,
                    ),
                ],
                spacing=4,
                expand=True,
            ),
        ]

        if acao is not None:
            controles.append(
                ft.Icon(
                    ft.Icons.EDIT_OUTLINED,
                    color=C.PRIMARY,
                )
            )

        return ft.Container(
            bgcolor=C.SURFACE,
            border_radius=12,
            padding=16,
            on_click=acao,
            content=ft.Row(
                controls=controles,
                spacing=14,
            ),
        )

    # =========================================
    # AVATAR
    # =========================================

    dados_foto = usuario.get("_foto_bytes", foto_bytes)

    if dados_foto:
        avatar = ft.Image(
            src=dados_foto,
            width=100,
            height=100,
            fit=ft.BoxFit.COVER,
            border_radius=50,
            gapless_playback=True,
        )
    else:
        avatar = ft.Icon(
            ft.Icons.ACCOUNT_CIRCLE,
            size=100,
            color=C.PRIMARY,
        )

    # =========================================
    # CABEÇALHO
    # =========================================

    cabecalho = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                icon_color=C.TEXT,
                on_click=executar_voltar,
            ),
            ft.Text(
                "Meu perfil",
                size=22,
                weight=ft.FontWeight.BOLD,
                color=C.TEXT,
            ),
            ft.Container(width=40),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # =========================================
    # IDENTIFICAÇÃO
    # =========================================

    controles_identificacao = [
        avatar,
        ft.Text(
            nome,
            size=23,
            weight=ft.FontWeight.BOLD,
            color=C.TEXT,
            text_align=ft.TextAlign.CENTER,
        ),
        ft.Text(
            nome_funcao,
            size=14,
            color=C.TEXT_SECONDARY,
        ),
        ft.Container(height=8),
        ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CAMERA_ALT_OUTLINED),
                    ft.Text("Alterar foto"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8,
            ),
            on_click=escolher_foto,
        ),
    ]

    if dados_foto:
        controles_identificacao.append(
            ft.TextButton(
                "Remover foto",
                on_click=excluir_foto,
            )
        )

    identificacao = ft.Container(
        bgcolor=C.SURFACE,
        border_radius=16,
        padding=24,
        content=ft.Column(
            controls=controles_identificacao,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
    )

    # =========================================
    # BOTÃO SAIR
    # =========================================

    botao_sair = ft.Button(
        content=ft.Row(
            controls=[
                ft.Icon(
                    ft.Icons.LOGOUT,
                    color=C.TEXT,
                ),
                ft.Text(
                    "Sair da conta",
                    color=C.TEXT,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        on_click=executar_sair,
    )

    # =========================================
    # CONTEÚDO
    # =========================================

    conteudo = ft.Column(
        controls=[
            cabecalho,
            ft.Container(height=16),
            identificacao,
            ft.Container(height=18),

            ft.Text(
                "INFORMAÇÕES DA CONTA",
                size=13,
                weight=ft.FontWeight.BOLD,
                color=C.PRIMARY,
            ),

            campo_informacao(
                "Nome",
                nome,
                ft.Icons.PERSON_OUTLINE,
                acao=abrir_edicao,
            ),

            campo_informacao(
                "E-mail",
                email,
                ft.Icons.EMAIL_OUTLINED,
            ),

            campo_informacao(
                "Nível de acesso",
                nome_funcao,
                ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
            ),

            ft.Container(height=14),

            ft.Text(
                "SEGURANÇA DA CONTA",
                size=13,
                weight=ft.FontWeight.BOLD,
                color=C.PRIMARY,
            ),

            campo_informacao(
                "Senha",
                "Alterar senha de acesso",
                ft.Icons.LOCK_OUTLINE,
                acao=abrir_alteracao_senha,
            ),

            ft.Container(height=18),
            botao_sair,
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    # =========================================
    # EXIBIR TELA
    # =========================================

    page.clean()
    page.bgcolor = C.BACKGROUND
    page.padding = 16
    page.navigation_bar = None
    page.drawer = None

    page.add(
        ft.SafeArea(
            content=conteudo,
            expand=True,
        )
    )

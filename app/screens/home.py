
import flet as ft

from app.theme.colors import AppColors as C


def home_screen(
    page: ft.Page,
    abrir_comandas=None,
    abrir_fechadas=None,
    abrir_nova=None,
    abrir_cardapio=None,
    abrir_analises=None,
    usuario=None,
    abrir_perfil=None,
):
    usuario = usuario or {}

    nome = usuario.get("nome") or "Usuário"
    funcao = usuario.get("funcao", "atendente")
    administrador = funcao == "admin"
    foto_bytes = usuario.get("_foto_bytes")

    nome_funcao = (
        "Administrador" if administrador else "Funcionário"
    )

    # =========================================
    # MENSAGENS
    # =========================================

    def mostrar_mensagem(texto):
        page.show_dialog(
            ft.SnackBar(
                content=ft.Text(texto)
            )
        )

    # =========================================
    # EXECUTAR AÇÕES
    # =========================================

    def executar_acao(acao, titulo):
        if acao is not None:
            acao()
        else:
            mostrar_mensagem(
                f"{titulo}: funcionalidade em desenvolvimento."
            )

    # =========================================
    # FOTO DE PERFIL
    # =========================================

    def criar_avatar(tamanho):
        if foto_bytes:
            return ft.Image(
                src=foto_bytes,
                width=tamanho,
                height=tamanho,
                fit=ft.BoxFit.COVER,
                border_radius=tamanho / 2,
                gapless_playback=True,
            )

        return ft.Icon(
            ft.Icons.ACCOUNT_CIRCLE,
            size=tamanho,
            color=C.PRIMARY,
        )

    # =========================================
    # CRIAR ATALHOS
    # =========================================

    def criar_atalho(
        titulo,
        icone,
        acao=None,
        destaque=False,
        subtitulo=None,
    ):
        cor_fundo = C.PRIMARY if destaque else C.SURFACE
        cor_texto = C.BACKGROUND if destaque else C.TEXT

        conteudo = [
            ft.Icon(
                icone,
                size=34,
                color=cor_texto,
            ),
            ft.Text(
                titulo,
                size=15,
                weight=ft.FontWeight.BOLD,
                color=cor_texto,
                text_align=ft.TextAlign.CENTER,
            ),
        ]

        if subtitulo:
            conteudo.append(
                ft.Text(
                    subtitulo,
                    color=cor_texto,
                    size=12,
                    text_align=ft.TextAlign.CENTER,
                )
            )

        return ft.Container(
            content=ft.Column(
                controls=conteudo,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=cor_fundo,
            border_radius=14,
            padding=14,
            height=145,
            expand=True,
            on_click=lambda e: executar_acao(
                acao,
                titulo.replace("\n", " "),
            ),
        )

    # =========================================
    # MENU LATERAL DESLIZANTE
    # =========================================

    async def abrir_menu(e=None):
        await page.show_drawer()

    def navegar_menu(acao, titulo):
        executar_acao(acao, titulo)

    destinos_menu = [
        ft.NavigationDrawerDestination(
            icon=ft.Icons.HOME_OUTLINED,
            selected_icon=ft.Icons.HOME,
            label="Início",
        ),
        ft.NavigationDrawerDestination(
            icon=ft.Icons.RECEIPT_LONG_OUTLINED,
            selected_icon=ft.Icons.RECEIPT_LONG,
            label="Comandas abertas",
        ),
        ft.NavigationDrawerDestination(
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            label="Comandas fechadas",
        ),
        ft.NavigationDrawerDestination(
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            label="Novo pedido",
        ),
    ]

    acoes_menu = [
        None,
        abrir_comandas,
        abrir_fechadas,
        abrir_nova,
    ]

    titulos_menu = [
        "Início",
        "Comandas abertas",
        "Comandas fechadas",
        "Novo pedido",
    ]

    # =========================================
    # OPÇÕES DO ADMINISTRADOR
    # =========================================

    if administrador:
        destinos_menu.extend([
            ft.NavigationDrawerDestination(
                icon=ft.Icons.RESTAURANT_MENU,
                label="Gerenciar cardápio",
            ),
            ft.NavigationDrawerDestination(
                icon=ft.Icons.BAR_CHART,
                label="Análises de vendas",
            ),
        ])

        acoes_menu.extend([
            abrir_cardapio,
            abrir_analises,
        ])

        titulos_menu.extend([
            "Gerenciar cardápio",
            "Análises de vendas",
        ])

    # =========================================
    # PERFIL NO MENU
    # =========================================

    destinos_menu.append(
        ft.NavigationDrawerDestination(
            icon=ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
            label="Meu perfil",
        )
    )

    acoes_menu.append(abrir_perfil)
    titulos_menu.append("Meu perfil")

    # =========================================
    # SELEÇÃO DO MENU
    # =========================================

    async def selecionar_item_menu(e):
        indice = e.control.selected_index

        if indice < 0 or indice >= len(acoes_menu):
            return

        await page.close_drawer()

        if indice == 0:
            return

        navegar_menu(
            acoes_menu[indice],
            titulos_menu[indice],
        )

    # =========================================
    # CABEÇALHO DO MENU HAMBÚRGUER
    # =========================================

    cabecalho_menu = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                criar_avatar(72),
                ft.Text(
                    nome,
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=C.TEXT,
                ),
                ft.Text(
                    nome_funcao,
                    size=12,
                    color=C.TEXT_SECONDARY,
                ),
            ],
            spacing=8,
        ),
    )

    menu_lateral = ft.NavigationDrawer(
        bgcolor=C.SURFACE,
        selected_index=0,
        on_change=selecionar_item_menu,
        controls=[
            cabecalho_menu,
            ft.Divider(color=C.BORDER),
            *destinos_menu,
        ],
    )

    # =========================================
    # CABEÇALHO DA HOME
    # =========================================

    botao_perfil = ft.Container(
        width=46,
        height=46,
        border_radius=23,
        alignment=ft.Alignment.CENTER,
        content=criar_avatar(42),
        on_click=lambda e: executar_acao(
            abrir_perfil,
            "Meu perfil",
        ),
        tooltip="Meu perfil",
    )

    cabecalho = ft.Row(
        controls=[
            ft.IconButton(
                icon=ft.Icons.MENU,
                icon_color=C.TEXT,
                on_click=abrir_menu,
            ),
            ft.Column(
                controls=[
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
            botao_perfil,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    # =========================================
    # ATALHOS PRINCIPAIS
    # =========================================

    atalhos = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    criar_atalho(
                        "Comandas\nAbertas",
                        ft.Icons.RECEIPT_LONG,
                        acao=abrir_comandas,
                        destaque=True,
                    ),
                    criar_atalho(
                        "Comandas\nFechadas",
                        ft.Icons.CHECK_CIRCLE_OUTLINE,
                        acao=abrir_fechadas,
                    ),
                ],
                spacing=12,
            ),
            ft.Row(
                controls=[
                    criar_atalho(
                        "Novo Pedido",
                        ft.Icons.ADD_CIRCLE_OUTLINE,
                        acao=abrir_nova,
                    ),
                ],
                spacing=12,
            ),
        ],
        spacing=12,
    )

    # =========================================
    # ÁREA ADMINISTRATIVA
    # =========================================

    if administrador:
        atalhos.controls.append(
            ft.Container(
                padding=ft.Padding.only(top=12),
                content=ft.Text(
                    "ADMINISTRAÇÃO",
                    size=13,
                    weight=ft.FontWeight.BOLD,
                    color=C.PRIMARY,
                ),
            )
        )

        atalhos.controls.append(
            ft.Row(
                controls=[
                    criar_atalho(
                        "Gerenciar\nCardápio",
                        ft.Icons.RESTAURANT_MENU,
                        acao=abrir_cardapio,
                    ),
                    criar_atalho(
                        "Análises de\nVendas",
                        ft.Icons.BAR_CHART,
                        acao=abrir_analises,
                    ),
                ],
                spacing=12,
            )
        )

    # =========================================
    # NAVEGAÇÃO INFERIOR
    # =========================================

    async def mudar_navegacao(e):
        indice = e.control.selected_index

        if indice == 0:
            return

        if indice == 1:
            executar_acao(
                abrir_comandas,
                "Pedidos",
            )
        else:
            await abrir_menu()

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
        on_change=mudar_navegacao,
    )

    # =========================================
    # CONTEÚDO PRINCIPAL
    # =========================================

    conteudo = ft.Column(
        controls=[
            cabecalho,
            ft.Container(height=22),
            ft.Text(
                f"Olá, {nome}!",
                size=25,
                weight=ft.FontWeight.BOLD,
                color=C.TEXT,
            ),
            ft.Text(
                (
                    "Painel administrativo"
                    if administrador
                    else "Vamos deixar o dia ainda mais saboroso?"
                ),
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

    # =========================================
    # EXIBIR TELA
    # =========================================

    page.clean()
    page.bgcolor = C.BACKGROUND
    page.padding = 16
    page.navigation_bar = navegacao
    page.drawer = menu_lateral

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

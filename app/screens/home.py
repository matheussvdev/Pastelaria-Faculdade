
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
    primeiro_nome = nome.split()[0]
    administrador = usuario.get("funcao") == "admin"
    foto_bytes = usuario.get("_foto_bytes")

    nome_funcao = (
        "Administrador" if administrador else "Funcionário"
    )

    FUNDO = C.BACKGROUND
    SUPERFICIE = C.SURFACE
    AMARELO = C.PRIMARY
    TEXTO = C.TEXT
    SECUNDARIO = C.TEXT_SECONDARY
    BORDA = C.BORDER
    VERMELHO = C.RED

    def criar_borda(cor, largura=1):
        lado = ft.BorderSide(width=largura, color=cor)
        return ft.Border(
            left=lado,
            top=lado,
            right=lado,
            bottom=lado,
        )

    def mostrar_mensagem(texto):
        page.show_dialog(
            ft.SnackBar(content=ft.Text(texto))
        )

    def executar_acao(acao, titulo):
        if acao is not None:
            acao()
        else:
            mostrar_mensagem(
                f"{titulo}: funcionalidade em desenvolvimento."
            )

    # =========================================
    # AVATAR
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
            color=AMARELO,
        )

    # =========================================
    # CARTÕES DE ATALHO
    # =========================================

    def criar_atalho(
        titulo,
        descricao,
        icone,
        acao,
        cor_icone=None,
    ):
        cor_icone = cor_icone or AMARELO

        return ft.Container(
            expand=True,
            height=172,
            bgcolor=SUPERFICIE,
            border=criar_borda(BORDA),
            border_radius=18,
            padding=16,
            on_click=lambda e: executar_acao(acao, titulo),
            content=ft.Column(
                controls=[
                    ft.Container(
                        width=48,
                        height=48,
                        bgcolor=FUNDO,
                        border_radius=14,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(
                            icone,
                            size=27,
                            color=cor_icone,
                        ),
                    ),
                    ft.Text(
                        titulo,
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=TEXTO,
                        max_lines=2,
                    ),
                    ft.Text(
                        descricao,
                        size=11,
                        color=SECUNDARIO,
                        max_lines=2,
                    ),
                ],
                spacing=9,
            ),
        )

    # =========================================
    # MENU LATERAL
    # =========================================

    async def abrir_menu(e=None):
        await page.show_drawer()

    destinos_menu = [
        ft.NavigationDrawerDestination(
            icon=ft.Icons.HOME_OUTLINED,
            selected_icon=ft.Icons.HOME,
            label="Início",
        ),
        ft.NavigationDrawerDestination(
            icon=ft.Icons.RECEIPT_LONG_OUTLINED,
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

    destinos_menu.append(
        ft.NavigationDrawerDestination(
            icon=ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
            label="Meu perfil",
        )
    )

    acoes_menu.append(abrir_perfil)
    titulos_menu.append("Meu perfil")

    async def selecionar_item_menu(e):
        indice = e.control.selected_index

        if indice < 0 or indice >= len(acoes_menu):
            return

        await page.close_drawer()

        if indice == 0:
            return

        executar_acao(
            acoes_menu[indice],
            titulos_menu[indice],
        )

    cabecalho_menu = ft.Container(
        padding=20,
        content=ft.Column(
            controls=[
                criar_avatar(72),
                ft.Text(
                    nome,
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=TEXTO,
                ),
                ft.Text(
                    nome_funcao,
                    size=12,
                    color=SECUNDARIO,
                ),
            ],
            spacing=8,
        ),
    )

    menu_lateral = ft.NavigationDrawer(
        bgcolor=SUPERFICIE,
        selected_index=0,
        on_change=selecionar_item_menu,
        controls=[
            cabecalho_menu,
            ft.Divider(color=BORDA),
            *destinos_menu,
        ],
    )

    # =========================================
    # CABEÇALHO
    # =========================================

    botao_perfil = ft.Container(
        width=48,
        height=48,
        border_radius=24,
        border=criar_borda(BORDA),
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
                icon_color=TEXTO,
                on_click=abrir_menu,
            ),
            ft.Column(
                controls=[
                    ft.Text(
                        "PASTELARIA",
                        size=21,
                        weight=ft.FontWeight.BOLD,
                        color=TEXTO,
                    ),
                    ft.Text(
                        "SABOR EM CADA MORDIDA",
                        size=9,
                        color=AMARELO,
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
    # BOAS-VINDAS
    # =========================================

    boas_vindas = ft.Column(
        controls=[
            ft.Text(
                f"Olá, {primeiro_nome}!",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=TEXTO,
            ),
            ft.Text(
                (
                    "Gerencie sua pastelaria com praticidade."
                    if administrador
                    else "Pronto para mais um dia de atendimento?"
                ),
                size=13,
                color=SECUNDARIO,
            ),
            ft.Container(
                padding=ft.Padding.symmetric(
                    horizontal=12,
                    vertical=7,
                ),
                bgcolor=SUPERFICIE,
                border_radius=20,
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.VERIFIED_USER_OUTLINED,
                            size=16,
                            color=AMARELO,
                        ),
                        ft.Text(
                            nome_funcao,
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=AMARELO,
                        ),
                    ],
                    spacing=7,
                    tight=True,
                ),
            ),
        ],
        spacing=9,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )

    # =========================================
    # AÇÃO PRINCIPAL
    # =========================================

    novo_pedido = ft.Container(
        bgcolor=AMARELO,
        border_radius=20,
        padding=20,
        on_click=lambda e: executar_acao(
            abrir_nova,
            "Novo pedido",
        ),
        content=ft.Row(
            controls=[
                ft.Container(
                    width=56,
                    height=56,
                    border_radius=16,
                    bgcolor=FUNDO,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(
                        ft.Icons.ADD_SHOPPING_CART,
                        size=29,
                        color=AMARELO,
                    ),
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            "Novo pedido",
                            size=19,
                            weight=ft.FontWeight.BOLD,
                            color=FUNDO,
                        ),
                        ft.Text(
                            "Registrar uma nova comanda",
                            size=12,
                            color=FUNDO,
                        ),
                    ],
                    spacing=4,
                    expand=True,
                ),
                ft.Icon(
                    ft.Icons.ARROW_FORWARD_IOS,
                    color=FUNDO,
                    size=18,
                ),
            ],
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    # =========================================
    # COMANDAS
    # =========================================

    secao_comandas = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(
                        "Gerenciar comandas",
                        size=19,
                        weight=ft.FontWeight.BOLD,
                        color=TEXTO,
                    ),
                    ft.Icon(
                        ft.Icons.RECEIPT_LONG_OUTLINED,
                        size=20,
                        color=AMARELO,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Row(
                controls=[
                    criar_atalho(
                        "Comandas abertas",
                        "Pedidos em andamento",
                        ft.Icons.RECEIPT_LONG,
                        abrir_comandas,
                        AMARELO,
                    ),
                    criar_atalho(
                        "Comandas fechadas",
                        "Histórico de pedidos",
                        ft.Icons.CHECK_CIRCLE_OUTLINE,
                        abrir_fechadas,
                        VERMELHO,
                    ),
                ],
                spacing=12,
            ),
        ],
        spacing=14,
    )

    # =========================================
    # ADMINISTRAÇÃO
    # =========================================

    secao_admin = None

    if administrador:
        secao_admin = ft.Column(
            controls=[
                ft.Divider(color=BORDA),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Administração",
                            size=19,
                            weight=ft.FontWeight.BOLD,
                            color=TEXTO,
                        ),
                        ft.Icon(
                            ft.Icons.ADMIN_PANEL_SETTINGS_OUTLINED,
                            color=AMARELO,
                            size=22,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Text(
                    "Ferramentas exclusivas do administrador",
                    size=12,
                    color=SECUNDARIO,
                ),
                ft.Row(
                    controls=[
                        criar_atalho(
                            "Gerenciar cardápio",
                            "Produtos e preços",
                            ft.Icons.RESTAURANT_MENU,
                            abrir_cardapio,
                            AMARELO,
                        ),
                        criar_atalho(
                            "Análises de vendas",
                            "Resultados do negócio",
                            ft.Icons.BAR_CHART,
                            abrir_analises,
                            VERMELHO,
                        ),
                    ],
                    spacing=12,
                ),
            ],
            spacing=12,
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
        bgcolor=FUNDO,
        indicator_color=SUPERFICIE,
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

    controles = [
        cabecalho,
        ft.Container(height=16),
        boas_vindas,
        ft.Container(height=16),
        novo_pedido,
        ft.Container(height=16),
        secao_comandas,
    ]

    if secao_admin is not None:
        controles.extend([
            ft.Container(height=18),
            secao_admin,
        ])

    controles.append(ft.Container(height=20))

    conteudo = ft.Column(
        controls=controles,
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    page.clean()
    page.bgcolor = FUNDO
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

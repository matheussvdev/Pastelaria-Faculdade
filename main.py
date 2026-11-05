
import flet as ft

from app.services.supabase_client import criar_cliente_supabase
from app.services.produtos_service import listar_produtos
from app.services.comandas_service import (
    criar_comanda_bd,
    buscar_detalhes_comanda_bd,
    adicionar_itens_comanda_bd,
)
from app.services.foto_perfil_service import (
    enviar_foto_perfil,
    carregar_foto_perfil,
    remover_foto_perfil,
)

from app.screens.login import login_screen
from app.screens.home import home_screen
from app.screens.comandas_abertas import comandas_abertas_screen
from app.screens.comandas_fechadas import comandas_fechadas_screen
from app.screens.detalhes_comanda import detalhes_comanda_screen
from app.screens.nova_comanda import nova_comanda_screen
from app.screens.gerenciar_cardapio import gerenciar_cardapio_screen
from app.screens.analises_vendas import analises_vendas_screen
from app.screens.perfil import perfil_screen


def main(page: ft.Page):
    page.title = "Pastelaria"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0B0B0D"

    cliente_supabase = criar_cliente_supabase()
    usuario_atual = None

    # =========================================
    # CARREGAMENTO DA FOTO
    # =========================================

    def garantir_foto_carregada():
        if usuario_atual is None:
            return

        caminho = usuario_atual.get("foto_path")

        if not caminho:
            usuario_atual["_foto_bytes"] = None
            return

        if usuario_atual.get("_foto_bytes") is not None:
            return

        try:
            usuario_atual["_foto_bytes"] = carregar_foto_perfil(
                cliente_supabase,
                caminho,
            )
        except Exception as erro:
            print(f"Erro ao carregar foto: {erro}")

    # =========================================
    # AUTENTICAÇÃO
    # =========================================

    def autenticar(email, senha):
        nonlocal usuario_atual

        resposta = cliente_supabase.auth.sign_in_with_password({
            "email": email,
            "password": senha,
        })

        if resposta.user is None:
            raise ValueError("Falha na autenticação.")

        perfil = (
            cliente_supabase.table("perfis")
            .select("nome, funcao, foto_path")
            .eq("id", resposta.user.id)
            .single()
            .execute()
        )

        if not perfil.data:
            cliente_supabase.auth.sign_out()
            raise ValueError("Perfil não encontrado.")

        usuario_atual = {
            **perfil.data,
            "email": resposta.user.email or email,
            "_foto_bytes": None,
        }

        abrir_inicio()

    # =========================================
    # HOME
    # =========================================

    def abrir_inicio():
        garantir_foto_carregada()

        home_screen(
            page,
            abrir_comandas=abrir_comandas,
            abrir_fechadas=abrir_fechadas,
            abrir_nova=abrir_nova,
            abrir_cardapio=abrir_cardapio,
            abrir_analises=abrir_analises,
            abrir_perfil=abrir_perfil,
            usuario=usuario_atual,
        )

    # =========================================
    # COMANDAS
    # =========================================

    def abrir_comandas():
        comandas_abertas_screen(
            page,
            voltar=abrir_inicio,
            abrir_detalhes=abrir_detalhes,
            abrir_nova=abrir_nova,
            cliente_supabase=cliente_supabase,
        )

    def abrir_fechadas():
        comandas_fechadas_screen(
            page,
            voltar=abrir_inicio,
            abrir_detalhes=abrir_detalhes,
            cliente_supabase=cliente_supabase,
        )

    def abrir_detalhes(comanda):
        fechada = comanda["status"] == "fechada"

        detalhes_comanda_screen(
            page,
            comanda=comanda,
            voltar=abrir_fechadas if fechada else abrir_comandas,
            atualizar=abrir_comandas,
            adicionar_itens=lambda: abrir_nova(comanda),
            cliente_supabase=cliente_supabase,
        )

    def abrir_nova(comanda=None):
        try:
            produtos = listar_produtos(cliente_supabase)
        except Exception as erro:
            print(f"Erro ao carregar produtos: {erro}")

            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(
                        "Não foi possível carregar o cardápio."
                    )
                )
            )
            return

        def salvar_comanda(nome_cliente, itens):
            if comanda is None:
                comanda_id = criar_comanda_bd(
                    cliente_supabase,
                    nome_cliente,
                    itens,
                )
            else:
                comanda_id = int(comanda["id"])

                adicionar_itens_comanda_bd(
                    cliente_supabase,
                    comanda_id,
                    itens,
                )

            detalhes = buscar_detalhes_comanda_bd(
                cliente_supabase,
                comanda_id,
            )

            abrir_detalhes(detalhes)

        nova_comanda_screen(
            page,
            voltar=(
                (lambda: abrir_detalhes(comanda))
                if comanda
                else abrir_comandas
            ),
            salvar=salvar_comanda,
            comanda=comanda,
            cardapio=produtos,
        )

    # =========================================
    # ADMINISTRAÇÃO
    # =========================================

    def abrir_cardapio():
        if (
            usuario_atual is None
            or usuario_atual.get("funcao") != "admin"
        ):
            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(
                        "Acesso exclusivo do administrador."
                    )
                )
            )
            return

        gerenciar_cardapio_screen(
            page,
            voltar=abrir_inicio,
            cliente_supabase=cliente_supabase,
        )

    def abrir_analises():
        if (
            usuario_atual is None
            or usuario_atual.get("funcao") != "admin"
        ):
            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(
                        "Acesso exclusivo do administrador."
                    )
                )
            )
            return

        analises_vendas_screen(
            page,
            voltar=abrir_inicio,
            cliente_supabase=cliente_supabase,
        )

    # =========================================
    # ALTERAR NOME
    # =========================================

    def salvar_nome_perfil(novo_nome):
        nonlocal usuario_atual

        if usuario_atual is None:
            raise ValueError("Usuário não autenticado.")

        nome_validado = novo_nome.strip()

        if not 3 <= len(nome_validado) <= 100:
            raise ValueError(
                "O nome deve ter entre 3 e 100 caracteres."
            )

        cliente_supabase.rpc(
            "atualizar_meu_nome",
            {"novo_nome": nome_validado},
        ).execute()

        usuario_atual["nome"] = nome_validado

    # =========================================
    # ALTERAR FOTO
    # =========================================

    def salvar_foto_usuario(nome_arquivo, dados):
        nonlocal usuario_atual

        if usuario_atual is None:
            raise ValueError("Usuário não autenticado.")

        caminho = enviar_foto_perfil(
            cliente_supabase,
            nome_arquivo,
            dados,
        )

        usuario_atual["foto_path"] = caminho
        usuario_atual["_foto_bytes"] = dados

    def remover_foto_usuario():
        nonlocal usuario_atual

        if usuario_atual is None:
            raise ValueError("Usuário não autenticado.")

        caminho = usuario_atual.get("foto_path")

        remover_foto_perfil(
            cliente_supabase,
            caminho,
        )

        usuario_atual["foto_path"] = None
        usuario_atual["_foto_bytes"] = None

    # =========================================
    # PERFIL
    # =========================================

    def abrir_perfil():
        if usuario_atual is None:
            abrir_login()
            return

        garantir_foto_carregada()

        perfil_screen(
            page,
            usuario=usuario_atual,
            voltar=abrir_inicio,
            sair=sair_da_conta,
            salvar_nome=salvar_nome_perfil,
            salvar_foto=salvar_foto_usuario,
            remover_foto=remover_foto_usuario,
            foto_bytes=usuario_atual.get("_foto_bytes"),
        )

    # =========================================
    # LOGIN E LOGOUT
    # =========================================

    def abrir_login():
        page.clean()
        page.navigation_bar = None
        page.drawer = None

        login_screen(
            page,
            autenticar=autenticar,
        )

    def sair_da_conta():
        nonlocal usuario_atual

        try:
            cliente_supabase.auth.sign_out()
        except Exception as erro:
            print(f"Erro ao sair da conta: {erro}")

            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(
                        "Não foi possível encerrar a sessão. "
                        "Tente novamente."
                    )
                )
            )
            return

        usuario_atual = None
        abrir_login()

    # =========================================
    # INICIAR
    # =========================================

    abrir_login()


ft.run(main)

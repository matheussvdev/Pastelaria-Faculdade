
import flet as ft

from app.screens.home import home_screen
from app.screens.comandas_abertas import comandas_abertas_screen
from app.screens.comandas_fechadas import comandas_fechadas_screen
from app.screens.detalhes_comanda import detalhes_comanda_screen
from app.screens.nova_comanda import nova_comanda_screen


def main(page: ft.Page):
    page.title = "Pastelaria"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0B0B0D"

    def abrir_inicio():
        home_screen(
            page,
            abrir_comandas=abrir_comandas,
            abrir_fechadas=abrir_fechadas,
        )

    def abrir_comandas():
        comandas_abertas_screen(
            page,
            voltar=abrir_inicio,
            abrir_detalhes=abrir_detalhes,
            abrir_nova=abrir_nova,
        )

    def abrir_fechadas():
        comandas_fechadas_screen(
            page,
            voltar=abrir_inicio,
            abrir_detalhes=abrir_detalhes,
        )

    def abrir_detalhes(comanda):
        fechada = comanda["status"] == "fechada"

        detalhes_comanda_screen(
            page,
            comanda=comanda,
            voltar=abrir_fechadas if fechada else abrir_comandas,
            atualizar=abrir_comandas,
            adicionar_itens=lambda: abrir_nova(comanda),
        )

    def abrir_nova(comanda=None):
        nova_comanda_screen(
            page,
            voltar=(
                (lambda: abrir_detalhes(comanda))
                if comanda else abrir_comandas
            ),
            salvar=abrir_detalhes,
            comanda=comanda,
        )

    abrir_inicio()


ft.run(main)

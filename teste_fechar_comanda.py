
from getpass import getpass

from app.services.supabase_client import criar_cliente_supabase
from app.services.comandas_service import (
    listar_comandas_abertas_bd,
    fechar_comanda_bd,
)


def main():
    cliente = criar_cliente_supabase()

    email = input("E-mail: ").strip()
    senha = getpass("Senha: ")

    try:
        cliente.auth.sign_in_with_password({
            "email": email,
            "password": senha,
        })

        comandas = listar_comandas_abertas_bd(cliente)

        if not comandas:
            print("Nenhuma comanda aberta.")
            return

        print("\nComandas abertas:")

        for comanda in comandas:
            print(
                f'#{comanda["id"]} - {comanda["cliente"]}'
            )

        identificador = int(
            input("\nID da comanda que deseja fechar: ")
        )

        comanda = next(
            (
                c for c in comandas
                if c["id"] == identificador
            ),
            None,
        )

        if comanda is None:
            print("Comanda não encontrada.")
            return

        confirmacao = input(
            f'Confirma o fechamento da comanda '
            f'#{identificador} de {comanda["cliente"]}? '
            f'(s/n): '
        ).strip().lower()

        if confirmacao != "s":
            print("Operação cancelada.")
            return

        total = fechar_comanda_bd(
            cliente,
            identificador,
        )

        print("\nComanda fechada com sucesso!")
        print(f"Total: R$ {total:.2f}")

        resposta = (
            cliente.table("comandas")
            .select("id, cliente, status, fechada_em")
            .eq("id", identificador)
            .single()
            .execute()
        )

        print("Registro atualizado:", resposta.data)

    except Exception as erro:
        print(f"Erro no fechamento: {erro}")

    finally:
        try:
            cliente.auth.sign_out()
        except Exception:
            pass


if __name__ == "__main__":
    main()

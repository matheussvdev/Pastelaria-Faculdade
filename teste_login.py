
from getpass import getpass

from app.services.supabase_client import criar_cliente_supabase


def main():
    print("=== TESTE DE LOGIN SUPABASE ===")

    email = input("E-mail: ").strip()
    senha = getpass("Senha: ")

    if not email or not senha:
        print("Informe o e-mail e a senha.")
        return

    try:
        cliente = criar_cliente_supabase()

        resposta = cliente.auth.sign_in_with_password({
            "email": email,
            "password": senha,
        })

        usuario = resposta.user

        if usuario is None:
            print("Não foi possível autenticar o usuário.")
            return

        print("\nLogin realizado com sucesso!")

        perfil = (
            cliente.table("perfis")
            .select("nome, funcao")
            .eq("id", usuario.id)
            .single()
            .execute()
        )

        print("Nome:", perfil.data["nome"])
        print("Função:", perfil.data["funcao"])

        cliente.auth.sign_out()

    except Exception as erro:
        print(f"\nErro na autenticação: {erro}")


if __name__ == "__main__":
    main()

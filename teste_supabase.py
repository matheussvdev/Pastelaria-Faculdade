
from app.services.supabase_client import criar_cliente_supabase


def main():
    try:
        cliente = criar_cliente_supabase()

        print("Cliente Supabase configurado com sucesso!")
        print("Pronto para autenticar um usuário.")

    except Exception as erro:
        print(f"Erro ao configurar Supabase: {erro}")


if __name__ == "__main__":
    main()

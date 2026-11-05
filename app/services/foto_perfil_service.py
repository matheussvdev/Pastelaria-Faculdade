
import io

BUCKET_FOTOS = "fotos-perfil"
TAMANHO_MAXIMO = 2 * 1024 * 1024

EXTENSOES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}


def obter_usuario_id(cliente_supabase):
    resposta = cliente_supabase.auth.get_user()

    if resposta is None or resposta.user is None:
        raise ValueError("Usuário não autenticado.")

    return str(resposta.user.id)


def identificar_imagem(dados):
    if dados.startswith(b"\xff\xd8\xff"):
        return "jpg", "image/jpeg"

    if dados.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png", "image/png"

    if (
        len(dados) >= 12
        and dados[:4] == b"RIFF"
        and dados[8:12] == b"WEBP"
    ):
        return "webp", "image/webp"

    raise ValueError(
        "Formato inválido. Escolha JPG, PNG ou WebP."
    )


def validar_imagem(nome_arquivo, dados):
    if not isinstance(dados, bytes):
        raise ValueError(
            "Não foi possível ler a imagem selecionada."
        )

    if len(dados) == 0:
        raise ValueError("A imagem está vazia.")

    if len(dados) > TAMANHO_MAXIMO:
        raise ValueError(
            "A imagem deve ter no máximo 2 MB."
        )

    extensao_nome = nome_arquivo.rsplit(".", 1)[-1].lower()

    if extensao_nome not in EXTENSOES:
        raise ValueError(
            "Escolha uma imagem JPG, PNG ou WebP."
        )

    extensao_real, tipo_mime = identificar_imagem(dados)

    if (
        extensao_nome in ("jpg", "jpeg")
        and extensao_real != "jpg"
    ):
        raise ValueError(
            "O conteúdo não corresponde à extensão do arquivo."
        )

    if (
        extensao_nome not in ("jpg", "jpeg")
        and extensao_nome != extensao_real
    ):
        raise ValueError(
            "O conteúdo não corresponde à extensão do arquivo."
        )

    # Confere se a imagem pode ser decodificada.
    try:
        from PIL import Image

        with Image.open(io.BytesIO(dados)) as imagem:
            imagem.verify()

    except ImportError:
        raise RuntimeError(
            "Instale Pillow com: pip install Pillow"
        )

    except Exception as erro:
        raise ValueError(
            "A imagem está corrompida ou é inválida."
        ) from erro

    return extensao_real, tipo_mime


def enviar_foto_perfil(
    cliente_supabase,
    nome_arquivo,
    dados,
):
    usuario_id = obter_usuario_id(cliente_supabase)

    extensao, tipo_mime = validar_imagem(
        nome_arquivo,
        dados,
    )

    caminho = f"{usuario_id}/avatar.{extensao}"

    # Consulta o caminho anterior para remover somente
    # arquivos que não são mais utilizados.
    perfil = (
        cliente_supabase.table("perfis")
        .select("foto_path")
        .eq("id", usuario_id)
        .single()
        .execute()
    )

    caminho_anterior = (
        perfil.data.get("foto_path")
        if perfil.data
        else None
    )

    armazenamento = cliente_supabase.storage.from_(
        BUCKET_FOTOS
    )

    armazenamento.upload(
        path=caminho,
        file=dados,
        file_options={
            "content-type": tipo_mime,
            "upsert": "true",
        },
    )

    # A função SQL atualiza apenas a foto
    # do próprio usuário autenticado.
    cliente_supabase.rpc(
        "atualizar_minha_foto",
        {"novo_foto_path": caminho},
    ).execute()

    # Exclui a foto antiga somente após salvar
    # a referência da nova foto com sucesso.
    if caminho_anterior and caminho_anterior != caminho:
        try:
            armazenamento.remove([caminho_anterior])
        except Exception as erro:
            print(
                f"Não foi possível remover a foto antiga: {erro}"
            )

    return caminho


def carregar_foto_perfil(
    cliente_supabase,
    caminho,
):
    if not caminho:
        return None

    usuario_id = obter_usuario_id(cliente_supabase)

    caminhos_permitidos = {
        f"{usuario_id}/avatar.jpg",
        f"{usuario_id}/avatar.png",
        f"{usuario_id}/avatar.webp",
    }

    if caminho not in caminhos_permitidos:
        raise ValueError(
            "Caminho da foto não autorizado."
        )

    dados = cliente_supabase.storage.from_(
        BUCKET_FOTOS
    ).download(caminho)

    return bytes(dados)


def remover_foto_perfil(
    cliente_supabase,
    caminho,
):
    usuario_id = obter_usuario_id(cliente_supabase)

    if caminho:
        caminhos_permitidos = {
            f"{usuario_id}/avatar.jpg",
            f"{usuario_id}/avatar.png",
            f"{usuario_id}/avatar.webp",
        }

        if caminho not in caminhos_permitidos:
            raise ValueError(
                "Caminho da foto não autorizado."
            )

    # Primeiro desvincula a foto do perfil.
    cliente_supabase.rpc(
        "atualizar_minha_foto",
        {"novo_foto_path": None},
    ).execute()

    if caminho:
        try:
            cliente_supabase.storage.from_(
                BUCKET_FOTOS
            ).remove([caminho])
        except Exception as erro:
            print(
                f"Foto desvinculada, mas não excluída: {erro}"
            )

from uuid import UUID

from contextos_de_negocio.barramento.bootstrap import bootstrap
from contextos_de_negocio.dominio.comandos.empresa import CadastrarEmpresa
from contextos_de_negocio.dominio.entidades.usuario import Usuario
from infra.banco_de_dados import (
    listar_schemas_existentes,
    excluir_schema,
)
from libs.utils.constantes import (
    SENHA_PRIMEIRO_USUARIO,
    EMAIL_PRIMEIRO_USUARIO,
    CPF_PRIMEIRO_USUARIO,
)


def gerar_usuario_fake_primeiro_cadastro(id_empresa: UUID) -> Usuario:
    usuario_fake = Usuario(
        empresa=id_empresa,
        nome="Usuario Fake",
        email=EMAIL_PRIMEIRO_USUARIO,
        cpf=CPF_PRIMEIRO_USUARIO,
        _senha=SENHA_PRIMEIRO_USUARIO,
        ativo=True,
        adm=True,
        permissoes=[],
        id=None,
    )
    return usuario_fake


async def criar_primeira_empresa_e_usuario() -> None:
    # verificar se algum schema é um uuid valido, se sim, não criar
    schemas = await listar_schemas_existentes()
    for schema in schemas:
        try:
            UUID(schema)
            return
        except ValueError:
            pass

    id_empresa = UUID(
        "7529b0ae-81ad-488b-b4ed-ecc094ca5084"
    )  # id fixo para primeira empesa
    usuario_fake = gerar_usuario_fake_primeiro_cadastro(id_empresa)
    bus = bootstrap(usuario=usuario_fake, schema=str(id_empresa), criar_schema=True)

    try:
        await bus.handle(
            CadastrarEmpresa(
                id=id_empresa,
                razao_social="JP ADM",
                nome_responsavel="João Campos",
                email=EMAIL_PRIMEIRO_USUARIO,
                senha=SENHA_PRIMEIRO_USUARIO,
                cpf=CPF_PRIMEIRO_USUARIO,
                ativo=True,
                cnpj="",
                nome_fantasia="JP ADM",
                deve_criar_usuario=True,
                _eh_primeira_empresa=True,
            )
        )
    except Exception as erro:
        await excluir_schema(str(id_empresa))
        print(f"Erro ao criar empresa. O schema {str(id_empresa)} foi dropado", erro)
        raise erro

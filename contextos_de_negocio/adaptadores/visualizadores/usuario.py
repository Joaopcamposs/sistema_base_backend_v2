from pydantic import UUID4

from contextos_de_negocio.dominio.entidades.usuario import Usuario
from libs.ddd.visualizadores.filtro import Filtros
from libs.utils.tipos_basicos import Email


async def listar_usuarios_por_id_e_email(
    unidade_de_trabalho: UnidadeDeTrabalho,
    id: UUID4 | None = None,
    email: str | None = None,
) -> list[Usuario]:
    from contextos_de_negocio import Dominio, UsuarioRepoConsulta

    filtros = Filtros(
        {
            "id": id,
            "email": Email(email),
        }
    )

    async with unidade_de_trabalho(Dominio.usuario) as uow:
        repo_consulta: UsuarioRepoConsulta = uow.view_repo

        usuarios = await repo_consulta.consultar_por_filtros(filtros=filtros)

    return usuarios

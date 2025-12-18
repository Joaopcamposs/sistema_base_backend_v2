from pydantic import UUID4

from contextos_de_negocio.barramento.unidade_de_trabalho import UnidadeDeTrabalho
from contextos_de_negocio.dominio.entidades.empresa import Empresa
from libs.ddd.visualizadores.filtro import Filtros


async def listar_empresas_por_id(
    unidade_de_trabalho: UnidadeDeTrabalho,
    id: UUID4 | None = None,
) -> list[Empresa]:
    from contextos_de_negocio import Dominio, EmpresaRepoConsulta

    filtros = Filtros(
        {
            "id": id,
        }
    )

    async with unidade_de_trabalho(Dominio.empresa) as uow:
        repo_consulta: EmpresaRepoConsulta = uow.view_repo

        empresas = await repo_consulta.consultar_por_filtros(filtros=filtros)

    return empresas

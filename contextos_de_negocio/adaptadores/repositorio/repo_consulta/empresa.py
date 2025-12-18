from uuid import UUID

from sqlalchemy import select

from contextos_de_negocio.adaptadores.orm.declarativo.empresa import EmpresaDB
from contextos_de_negocio.dominio.entidades.empresa import Empresa
from libs.ddd.adaptadores.repositorio import RepositorioConsulta
from libs.ddd.visualizadores.filtro import Filtros
from libs.utils.constantes import NAO_DELETADO
from libs.utils.tipos_basicos import Email, CPF, CNPJ


class EmpresaRepoConsulta(RepositorioConsulta):
    async def consultar_um_por_id(self, id: UUID) -> Empresa | None:
        async with self.session as session:
            empresa = (
                await session.execute(
                    select(EmpresaDB).where(
                        EmpresaDB.id == id, EmpresaDB.deletado_em.is_(None)
                    )
                )
            ).scalar_one_or_none()
            if not empresa:
                return None

            empresa_entidade = Empresa(
                razao_social=empresa.razao_social,
                nome_fantasia=empresa.nome_fantasia,
                nome_responsavel=empresa.nome_responsavel,
                email=Email(empresa.email),
                cpf=CPF(empresa.cpf),
                cnpj=CNPJ(empresa.cnpj),
                ativo=empresa.ativo,
                id=empresa.id,
            )

        return empresa_entidade

    async def consultar_um_por_filtros(self, filtros: Filtros) -> Empresa | None:
        async with self.session as session:
            empresa = (
                await session.execute(
                    select(EmpresaDB).filter_by(**filtros, **NAO_DELETADO)
                )
            ).scalar_one_or_none()
            if not empresa:
                return None

            empresa_entidade = Empresa(
                razao_social=empresa.razao_social,
                nome_fantasia=empresa.nome_fantasia,
                nome_responsavel=empresa.nome_responsavel,
                email=Email(empresa.email),
                cpf=CPF(empresa.cpf),
                cnpj=CNPJ(empresa.cnpj),
                ativo=empresa.ativo,
                id=empresa.id,
            )

        return empresa_entidade

    async def consultar_por_filtros(self, filtros: Filtros) -> list[Empresa]:
        async with self.session as session:
            empresas = (
                (
                    await session.execute(
                        select(EmpresaDB).filter_by(**filtros, **NAO_DELETADO)
                    )
                )
                .scalars()
                .all()
            )

            empresas_entidade = [
                Empresa(
                    razao_social=empresa.razao_social,
                    nome_fantasia=empresa.nome_fantasia,
                    nome_responsavel=empresa.nome_responsavel,
                    email=Email(empresa.email),
                    cpf=CPF(empresa.cpf),
                    cnpj=CNPJ(empresa.cnpj),
                    ativo=empresa.ativo,
                    id=empresa.id,
                )
                for empresa in empresas
            ]

        return empresas_entidade

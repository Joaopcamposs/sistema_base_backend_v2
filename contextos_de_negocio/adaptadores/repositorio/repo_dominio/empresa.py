from abc import abstractmethod
from typing import Any
from uuid import UUID

from sqlalchemy import select, insert, update, delete

from contextos_de_negocio.adaptadores.orm.declarativo.empresa import EmpresaDB
from contextos_de_negocio.dominio.agregados.empresa import Empresa
from contextos_de_negocio.dominio.excecoes import (
    EmpresaJaCadastrada,
    EmpresaNaoEncontrada,
)
from libs.ddd.adaptadores.repositorio import RepositorioDominio
from libs.ddd.visualizadores.filtro import Filtros

from libs.utils.constantes import NAO_DELETADO
from libs.utils.tipos_basicos import Email, TipoDeOperacao, CPF, CNPJ


class EmpresaRepoDominioAbstrato(RepositorioDominio):
    def __init__(self, *args: dict[str, Any], **kwargs: dict[str, Any]) -> None:
        super(EmpresaRepoDominioAbstrato, self).__init__(*args, **kwargs)
        self.seen: set[Empresa] = set()

    async def adicionar(self, empresa: Empresa) -> None:
        self.seen.add(empresa)
        await self._adicionar(empresa)

    @abstractmethod
    async def _adicionar(self, empresa: Empresa) -> None:
        raise NotImplementedError

    async def remover(self, empresa: Empresa) -> None:
        await self._remover(empresa)

    @abstractmethod
    async def _remover(self, empresa: Empresa) -> None:
        raise NotImplementedError

    @abstractmethod
    async def consultar_um_por_filtros(self, filtros: Filtros) -> Empresa:
        raise NotImplementedError()


class EmpresaRepoDominio(EmpresaRepoDominioAbstrato):
    async def gerar_agregado_para_cadastro(
        self,
        razao_social: str,
        nome_fantasia: str,
        nome_responsavel: str,
        email: Email,
        cpf: CPF,
        cnpj: CNPJ,
        ativo: bool,
        id: UUID | None = None,
        _eh_primeira_empresa: bool = False,
    ) -> Empresa:
        async with self.session as session:
            empresa_com_mesmo_email = (
                await session.execute(
                    select(EmpresaDB).where(
                        EmpresaDB.email == Email(email), EmpresaDB.deletado_em.is_(None)
                    )
                )
            ).scalar_one_or_none()
            if empresa_com_mesmo_email:
                raise EmpresaJaCadastrada

        return Empresa.retornar_agregado_para_cadastro(
            razao_social=razao_social,
            nome_fantasia=nome_fantasia,
            nome_responsavel=nome_responsavel,
            email=email,
            cpf=cpf,
            cnpj=cnpj,
            ativo=ativo,
            id=id,
            _eh_primeira_empresa=_eh_primeira_empresa,
        )

    async def consultar_um_por_filtros(self, filtros: Filtros) -> Empresa:
        async with self.session as session:
            empresa = (
                await session.execute(
                    select(EmpresaDB).filter_by(**filtros, **NAO_DELETADO)
                )
            ).scalar_one_or_none()
            if not empresa:
                raise EmpresaNaoEncontrada

            agregado = Empresa(
                razao_social=empresa.razao_social,
                nome_fantasia=empresa.nome_fantasia,
                nome_responsavel=empresa.nome_responsavel,
                email=Email(empresa.email),
                cpf=CPF(empresa.cpf),
                cnpj=CNPJ(empresa.cnpj),
                ativo=empresa.ativo,
                id=empresa.id,
                criado_por=empresa.criado_por,
                criado_em=empresa.criado_em,
                ultima_modificacao_em=empresa.ultima_modificacao_em,
                modificado_por=empresa.modificado_por,
                deletado_em=empresa.deletado_em,
                deletado_por=empresa.deletado_por,
            )

        return agregado

    async def _adicionar(
        self,
        empresa: Empresa,
    ) -> None:
        dados = {
            "id": empresa.id,
            "razao_social": empresa.razao_social,
            "nome_fantasia": empresa.nome_fantasia,
            "nome_responsavel": empresa.nome_responsavel,
            "email": empresa.email,
            "cpf": empresa.cpf,
            "cnpj": empresa.cnpj,
            "ativo": empresa.ativo,
            "criado_por": empresa.criado_por,
            "criado_em": empresa.criado_em,
            "modificado_por": empresa.modificado_por,
            "ultima_modificacao_em": empresa.ultima_modificacao_em,
            "deletado_por": empresa.deletado_por,
            "deletado_em": empresa.deletado_em,
        }

        match empresa._tipo_de_operacao:
            case TipoDeOperacao.INSERCAO:
                operacao = insert(EmpresaDB).values(dados)
            case TipoDeOperacao.ATUALIZACAO:
                operacao = (
                    update(EmpresaDB).where(EmpresaDB.id == empresa.id).values(dados)
                )
            case _:
                raise ValueError(
                    "Tipo de operação não suportado para o repositório de domínio."
                )

        await self.session.execute(operacao)

    async def _remover(self, empresa: Empresa) -> None:
        if empresa._usa_soft_delete:
            dados = {
                "modificado_por": empresa.modificado_por,
                "ultima_modificacao_em": empresa.ultima_modificacao_em,
                "deletado_por": empresa.deletado_por,
                "deletado_em": empresa.deletado_em,
            }

            operacao = update(EmpresaDB).where(EmpresaDB.id == empresa.id).values(dados)
        else:
            operacao = delete(EmpresaDB).where(EmpresaDB.id == empresa.id)

        await self.session.execute(operacao)

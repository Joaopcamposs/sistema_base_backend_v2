from __future__ import annotations
from abc import ABC
from typing import Callable, Any, Generator, TypeVar, Generic
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from contextos_de_negocio.dominio.entidades.usuario import Usuario
from infra.banco_de_dados.manipuladores_de_schemas import (
    criar_schema_completo_dentro_de_uma_transacao,
)
from libs.ddd.adaptadores.repositorio import RepositorioDominio, RepositorioConsulta


class UnidadeDeTrabalhoSchemaComProblema(Exception):
    pass


class TentandoAbrirUOWContextoJaAberto(Exception):
    pass


class UnidadeDeTrabalhoAbstrata(ABC):
    domain_repo: RepositorioDominio
    view_repo: RepositorioConsulta
    domain_repo_class: type[RepositorioDominio]
    view_repo_class: type[RepositorioConsulta]
    seen: set
    commited: bool
    session: AsyncSession
    session_leitura: AsyncSession
    usuario: Usuario | None
    schema: str | None = None
    criar_schema: bool = False

    eventos_fora_de_agregado: list["Evento"] = []  # noqa: F821

    def __init__(
        self,
        session_factory: Callable,
        usuario: Usuario | None = None,  # noqa: F821
        schema: str | None = None,
        criar_schema: bool = False,
    ) -> None:
        self.sql_session_factory = session_factory  # type: ignore[truthy-function]
        self.usuario = usuario
        self.criar_schema = criar_schema

        if (
            all(
                [
                    schema,
                    usuario,
                    str(usuario.empresa) != str(schema),  # type: ignore[union-attr]
                ]
            )
            and not criar_schema
        ):
            raise UnidadeDeTrabalhoSchemaComProblema(
                "O usuário não pertence a esse schema."
            )

        if not self.usuario:
            raise UnidadeDeTrabalhoSchemaComProblema(
                "Toda unidade de trabalho deve ter um usuario. "
                "Passe um usuário para a UnidadeDeTrabalho"
            )

        self.schema = schema or str(self.usuario.empresa)

        self.__contexto_ativo = False
        self.eventos_fora_de_agregado = []

    def __call__(
        self,
        repo_por_dominio: "Dominio" = None,  # noqa: F821
    ) -> UnidadeDeTrabalhoAbstrata:
        if repo_por_dominio:
            self.domain_repo_class = repo_por_dominio.value[0]
            self.view_repo_class = repo_por_dominio.value[1]
            self._nome_dominio_atual = repo_por_dominio.name

        return self

    async def __aenter__(self) -> UnidadeDeTrabalhoAbstrata:
        self.commited = False

        if self.__contexto_ativo is True:
            raise TentandoAbrirUOWContextoJaAberto()

        self.__contexto_ativo = True

        return self

    async def __aexit__(self, *args: dict[str, Any]) -> None:
        self.__contexto_ativo = False

        if not self.commited:
            await self.rollback()

        if hasattr(self, "session"):
            await self.session.close()

    def adicionar_evento_fora_de_agregado(self, evento: "Evento") -> None:  # noqa: F821
        self.eventos_fora_de_agregado.append(evento)

    def collect_new_events(self) -> Generator[Any, None, None]:
        if hasattr(self, "domain_repo") and self.domain_repo:
            for agregado in getattr(self.domain_repo, "seen", set()):
                while getattr(agregado, "eventos", []):
                    yield agregado.eventos.pop(0)

        if hasattr(self, "eventos_fora_de_agregado"):
            while self.eventos_fora_de_agregado:
                yield self.eventos_fora_de_agregado.pop(0)

    async def commit(self) -> None:
        await self.session.commit()
        self.commited = True

    async def rollback(self) -> None:
        if hasattr(self, "session"):
            await self.session.close()

    @property
    def empresa(self) -> UUID:
        if self.usuario and self.usuario.empresa:
            return self.usuario.empresa

        raise ValueError("Id da empresa não foi encontrado")


REPO_LEITURA = TypeVar("REPO_LEITURA")
REPO_ESCRITA = TypeVar("REPO_ESCRITA")


class UnidadeDeTrabalhoBase(
    UnidadeDeTrabalhoAbstrata, Generic[REPO_ESCRITA, REPO_LEITURA]
):
    domain_repo: RepositorioDominio
    view_repo: RepositorioConsulta

    def __init__(
        self,
        session_factory: Callable,
        engine_factory: Callable,
        base: type[DeclarativeBase],
        usuario: Usuario | None = None,
        schema: str | None = None,
        somente_leitura: bool = False,
        criar_schema: bool = False,
    ):
        self.somente_leitura = somente_leitura
        self.engine_factory = engine_factory
        self.base = base

        super().__init__(
            session_factory=session_factory,
            usuario=usuario,
            schema=schema,
            criar_schema=criar_schema,
        )

    async def __aenter__(self) -> UnidadeDeTrabalhoBase:
        self.commited = False

        if self.criar_schema:  # type: ignore[has-type]
            self.session = await criar_schema_completo_dentro_de_uma_transacao(
                engine_factory=self.engine_factory,
                base=self.base,
                schema_id=self.schema,
                session_factory=self.sql_session_factory,
            )
            self.criar_schema = False
        else:
            self.session = await self.sql_session_factory(
                somente_leitura=False,
                schema=self.schema,
            )
        self.session_leitura = await self.sql_session_factory(
            somente_leitura=True, schema=self.schema
        )

        if not self.somente_leitura and self.domain_repo_class:
            self.domain_repo = self.domain_repo_class(self.session)

        if self.view_repo_class:
            self.view_repo = self.view_repo_class(self.session_leitura)

        return await super().__aenter__()  # type: ignore[return-value]

    async def __aexit__(  # type: ignore[override]
        self, *args: tuple[type[Exception], Exception, Exception]
    ) -> None:
        await super().__aexit__(*args)

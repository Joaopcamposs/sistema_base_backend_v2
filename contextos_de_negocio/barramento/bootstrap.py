from typing import Callable

from sqlalchemy.orm import DeclarativeBase

from contextos_de_negocio.dominio.entidades.usuario import Usuario
from infra.banco_de_dados import sql_session_factory, get_sql_engine
from libs.ddd.adaptadores.orm import Base
from libs.ddd.barramento import (
    ManipuladoresDeEventos,
    ManipuladoresDeComandos,
    BarramentoDeMensagens,
)
from libs.ddd.bootstrap import bootstrap_base
from libs.ddd.unidade_de_trabalho import UnidadeDeTrabalhoBase


def bootstrap(
    session_factory: Callable = sql_session_factory,  # <== defina um session factory padrão
    engine_factory: Callable = get_sql_engine,  # <== defina um engine factory padrão
    base: type[DeclarativeBase] = Base,  # <== defina um base padrão
    event_handlers: ManipuladoresDeEventos | None = None,
    command_handlers: ManipuladoresDeComandos | None = None,
    uow: UnidadeDeTrabalhoBase | None = None,
    usuario: Usuario | None = None,
    schema: str | None = None,
    subir_erros_de_eventos: bool = False,
    somente_leitura: bool = False,
    criar_schema: bool = False,
) -> BarramentoDeMensagens:
    # importe seus manipuladores
    from contextos_de_negocio.barramento.manipuladores import (
        COMMAND_HANDLERS,
        EVENT_HANDLERS,
    )
    from contextos_de_negocio.barramento.unidade_de_trabalho import UnidadeDeTrabalho

    # defina seus manipuladores
    command_handlers = command_handlers or COMMAND_HANDLERS
    event_handlers = event_handlers or EVENT_HANDLERS

    if uow is None:
        uow = UnidadeDeTrabalho(
            usuario=usuario,
            schema=schema,
            somente_leitura=somente_leitura,
            criar_schema=criar_schema,
        )

    return bootstrap_base(
        uow=uow,
        session_factory=session_factory,
        engine_factory=engine_factory,
        base=base,
        event_handlers=event_handlers,
        command_handlers=command_handlers,
        usuario=usuario,
        schema=schema,
        subir_erros_de_eventos=subir_erros_de_eventos,
        somente_leitura=somente_leitura,
        criar_schema=criar_schema,
    )

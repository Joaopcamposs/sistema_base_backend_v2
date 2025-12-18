from sqlalchemy.orm import DeclarativeBase
import functools

import inspect
from typing import Any, Callable

from contextos_de_negocio.dominio.entidades.usuario import Usuario
from libs.ddd.barramento import (
    ManipuladoresDeComandos,
    ManipuladoresDeEventos,
    BarramentoDeMensagens,
    Comando,
    Evento,
    logger,
)
from libs.ddd.unidade_de_trabalho import UnidadeDeTrabalhoAbstrata, UnidadeDeTrabalhoBase


def bootstrap_abstrato(
    uow: UnidadeDeTrabalhoAbstrata,
    command_handlers: ManipuladoresDeComandos,
    event_handlers: ManipuladoresDeEventos,
    subir_erros_de_eventos: bool = False,
    permitir_execucoes_assincronas: bool = True,
) -> BarramentoDeMensagens:
    dependencies = {"uow": uow, "unidade_de_trabalho": uow}

    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies) for handler in event_handlers
        ]
        for event_type, event_handlers in event_handlers.items()
    }
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in command_handlers.items()
    }

    return BarramentoDeMensagens(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
        subir_erros_de_eventos=subir_erros_de_eventos,
        permitir_execucoes_assincronas=permitir_execucoes_assincronas,
    )


def inject_dependencies(handler: Callable, dependencies: dict) -> Callable:
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency for name, dependency in dependencies.items() if name in params
    }

    @functools.wraps(handler)
    async def async_wrapper(message: Comando | Evento) -> Any:
        try:
            return await handler(message, **deps)
        finally:
            logger.info(f"Handling async message {message} finished")

    return async_wrapper


def bootstrap_base(
    session_factory: Callable | None = None,
    engine_factory: Callable | None = None,
    base: type[DeclarativeBase] | None = None,
    uow: UnidadeDeTrabalhoAbstrata | None = None,
    usuario: Usuario | None = None,
    schema: str | None = None,
    event_handlers: ManipuladoresDeEventos | None = None,
    command_handlers: ManipuladoresDeComandos | None = None,
    subir_erros_de_eventos: bool = False,
    permitir_execucoes_assincronas: bool = True,
    somente_leitura: bool = False,
    criar_schema: bool = False,
) -> BarramentoDeMensagens:
    if uow is None:
        uow = UnidadeDeTrabalhoBase(
            session_factory=session_factory,
            engine_factory=engine_factory,
            base=base,
            usuario=usuario,
            schema=schema,
            somente_leitura=somente_leitura,
            criar_schema=criar_schema,
        )

    return bootstrap_abstrato(
        uow=uow,
        command_handlers=command_handlers,
        event_handlers=event_handlers,
        subir_erros_de_eventos=subir_erros_de_eventos,
        permitir_execucoes_assincronas=permitir_execucoes_assincronas,
    )

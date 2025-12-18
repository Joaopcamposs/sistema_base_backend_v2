"""Bootstrap para configuração do barramento de mensagens.

Este módulo fornece funções para configurar e inicializar o barramento
de mensagens com injeção de dependências.
"""

import functools
import inspect
import os
from typing import Any, Callable

from sqlalchemy.orm import DeclarativeBase

from contextos_de_negocio.dominio.entidades.usuario import Usuario
from libs.ddd.barramento import (
    ManipuladoresDeComandos,
    ManipuladoresDeEventos,
    BarramentoDeMensagens,
    Comando,
    Evento,
    DespachadorAssincrono,
    ReportadorDeErros,
    logger,
)
from libs.ddd.unidade_de_trabalho import UnidadeDeTrabalhoAbstrata, UnidadeDeTrabalhoBase


def _obter_despachador_padrao() -> DespachadorAssincrono | None:
    """Obtém despachador assíncrono padrão baseado no ambiente."""
    if os.getenv("TEST_ENV", "false") == "true":
        from libs.ddd.adaptadores.despachadores import DespachadorNulo

        return DespachadorNulo()

    try:
        from libs.ddd.adaptadores.despachadores import DespachadorCelery

        return DespachadorCelery()
    except ImportError:
        return None


def _obter_reportador_padrao() -> ReportadorDeErros | None:
    """Obtém reportador de erros padrão baseado no ambiente."""
    if os.getenv("TEST_ENV", "false") == "true":
        from libs.ddd.adaptadores.despachadores import ReportadorNulo

        return ReportadorNulo()

    if os.getenv("ENV_CONFIG", "development") in ["alpha", "production"]:
        try:
            from libs.ddd.adaptadores.despachadores import ReportadorSentry

            return ReportadorSentry()
        except ImportError:
            pass

    return None


def bootstrap_abstrato(
    uow: UnidadeDeTrabalhoAbstrata,
    command_handlers: ManipuladoresDeComandos,
    event_handlers: ManipuladoresDeEventos,
    subir_erros_de_eventos: bool = False,
    despachador_assincrono: DespachadorAssincrono | None = None,
    reportador_de_erros: ReportadorDeErros | None = None,
) -> BarramentoDeMensagens:
    """Configura o barramento com injeção de dependências nos handlers."""
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

    if despachador_assincrono is None:
        despachador_assincrono = _obter_despachador_padrao()

    if reportador_de_erros is None:
        reportador_de_erros = _obter_reportador_padrao()

    return BarramentoDeMensagens(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
        subir_erros_de_eventos=subir_erros_de_eventos,
        despachador_assincrono=despachador_assincrono,
        reportador_de_erros=reportador_de_erros,
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
    somente_leitura: bool = False,
    criar_schema: bool = False,
    despachador_assincrono: DespachadorAssincrono | None = None,
    reportador_de_erros: ReportadorDeErros | None = None,
) -> BarramentoDeMensagens:
    """Bootstrap base para configuração do barramento com SQLAlchemy."""
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
        despachador_assincrono=despachador_assincrono,
        reportador_de_erros=reportador_de_erros,
    )

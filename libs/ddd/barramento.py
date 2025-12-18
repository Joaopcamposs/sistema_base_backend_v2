import logging
from abc import ABC
from dataclasses import dataclass, asdict
from typing import Any, NewType, Callable

import sentry_sdk

from libs.ddd.unidade_de_trabalho import UnidadeDeTrabalhoAbstrata

logger = logging.getLogger(__name__)

CAMPOS_SENSIVEIS = frozenset({"senha", "token"})


@dataclass
class BaseComandoOuEvento(ABC):
    """Classe base para Comandos e Eventos com censura de campos sensíveis."""

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        if "__repr__" in cls.__dict__:
            cls.__repr__ = BaseComandoOuEvento.__repr__
        if "__str__" in cls.__dict__:
            cls.__str__ = BaseComandoOuEvento.__str__
        return super().__new__(cls)

    def __repr__(self) -> str:
        dados = asdict(self)
        for campo in CAMPOS_SENSIVEIS:
            if campo in dados:
                dados[campo] = "***"
        dados_str = ", ".join([f"{k}={v!r}" for k, v in dados.items()])
        return f"{self.__class__.__name__}({dados_str})"

    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class Comando(BaseComandoOuEvento):
    """Classe base para todos os comandos do sistema."""

    pass


@dataclass(kw_only=True)
class Evento(BaseComandoOuEvento):
    """
    Classe base para todos os eventos do sistema.

    Attributes:
        executar_de_forma_assincrona: Se True, o evento será processado de forma assíncrona.
    """

    executar_de_forma_assincrona: bool = False


Mensagem = Comando | Evento

ManipuladoresDeEventos = NewType(
    "ManipuladoresDeEventos", dict[type[Evento], list[Callable]]
)
ManipuladoresDeComandos = NewType(
    "ManipuladoresDeComandos", dict[type[Comando], Callable]
)


class BarramentoDeMensagens:
    def __init__(
        self,
        uow: UnidadeDeTrabalhoAbstrata,
        event_handlers: dict[type[Evento], list[Callable]],
        command_handlers: dict[type[Comando], Callable],
        subir_erros_de_eventos: bool = True,
        permitir_execucoes_assincronas: bool = False,
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers
        self.subir_erros_de_eventos = subir_erros_de_eventos
        self.permitir_execucoes_assincronas = permitir_execucoes_assincronas
        self.queue: list[Mensagem] = []

    async def handle(self, message: Mensagem) -> Any | None:
        self.queue = [message]

        command_result: Any | None = None

        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, Evento):
                await self.handle_event(message)
            elif isinstance(message, Comando):
                command_result = await self.handle_command(message)
            else:
                raise Exception(f"{message} was not an Event or Command")

        return command_result

    async def handle_event(self, event: Evento) -> None:
        if (
            self.permitir_execucoes_assincronas
            and isinstance(event, Evento)
            and event.executar_de_forma_assincrona
        ):
            await self.handle_async_event(event)
            return

        event_handlers = self.event_handlers.get(type(event)) or []
        for handler in event_handlers:
            try:
                logger.debug(f"handling event {event} with handler {handler}")
                await handler(event)
                self.queue.extend(self.uow.collect_new_events())
            except Exception as erro:
                logger.exception(f"Exception handling event {event}")

                import os
                from dotenv import load_dotenv

                load_dotenv()

                if (
                    self.subir_erros_de_eventos
                    or os.getenv("TEST_ENV", "false") == "true"
                ):
                    # We must raise erros in event handling if is running tests
                    raise erro

                if os.getenv("ENV_CONFIG", "development") in ["alpha", "production"]:
                    sentry_sdk.capture_exception(erro)

                continue

    async def handle_async_event(self, event: Evento) -> None:
        # from infra.aplicacoes.celery.tarefas import (
        #     task_tratar_evento_asyncrono,
        # )

        # tarefa = task_tratar_evento_asyncrono.si(
        #     evento=event,
        #     usuario=self.uow.usuario,
        # )
        #
        # if event.tempo_de_atraso_para_execucao_assincrona:
        #     tarefa = tarefa.set(countdown=event.tempo_de_atraso_para_execucao_assincrona)
        #
        # if event.fila_de_execucao_assincrona:
        #     tarefa = tarefa.set(queue=event.fila_de_execucao_assincrona)
        #
        #     if event.prioridade_de_execucao_assincrona:
        #         tarefa = tarefa.set(priority=event.prioridade_de_execucao_assincrona)
        #
        # tarefa.apply_async()
        ...

    async def handle_command(self, command: Comando) -> Any | None:
        logger.debug(f"handling command {command}")
        try:
            handler = self.command_handlers[type(command)]
            result = await handler(command)
            self.queue.extend(self.uow.collect_new_events())
            return result
        except Exception as erro:
            logger.exception(f"Exception handling command {command}")
            raise erro

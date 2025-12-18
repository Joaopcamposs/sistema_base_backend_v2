"""Barramento de mensagens para arquitetura DDD.

Este módulo implementa o padrão Message Bus para processamento de
comandos e eventos, seguindo os princípios do Domain-Driven Design.

O barramento é desacoplado de implementações específicas de filas
assíncronas (Celery, RabbitMQ, etc.) através de protocolos abstratos.
"""

import logging
import os
from abc import ABC
from dataclasses import dataclass, asdict
from typing import Any, NewType, Callable, Protocol, runtime_checkable

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


@runtime_checkable
class UnidadeDeTrabalhoProtocol(Protocol):
    """Protocolo para Unidade de Trabalho.

    Define a interface mínima necessária para o barramento funcionar,
    permitindo desacoplamento da implementação concreta.
    """

    usuario: Any

    def collect_new_events(self) -> Any:
        """Coleta novos eventos gerados pelos agregados."""
        ...


@runtime_checkable
class DespachadorAssincrono(Protocol):
    """Protocolo para despachadores de eventos assíncronos.

    Implementações podem usar Celery, RabbitMQ, SQS, etc.
    Isso permite trocar a implementação sem alterar o barramento.
    """

    def despachar(self, evento: Evento, usuario: Any) -> None:
        """Despacha um evento para processamento assíncrono."""
        ...


@runtime_checkable
class ReportadorDeErros(Protocol):
    """Protocolo para reportadores de erros.

    Implementações podem usar Sentry, Datadog, etc.
    """

    def capturar_excecao(self, erro: Exception) -> None:
        """Captura e reporta uma exceção."""
        ...


class BarramentoDeMensagens:
    """Barramento de mensagens para comandos e eventos.

    Processa comandos e eventos de forma síncrona, com suporte
    opcional para despacho assíncrono de eventos.

    Attributes:
        uow: Unidade de trabalho para gerenciar transações.
        event_handlers: Mapeamento de tipos de evento para handlers.
        command_handlers: Mapeamento de tipos de comando para handlers.
        subir_erros_de_eventos: Se True, levanta exceções em handlers de eventos.
        despachador_assincrono: Implementação do despachador assíncrono.
        reportador_de_erros: Implementação do reportador de erros.
    """

    def __init__(
        self,
        uow: UnidadeDeTrabalhoProtocol,
        event_handlers: dict[type[Evento], list[Callable]],
        command_handlers: dict[type[Comando], Callable],
        subir_erros_de_eventos: bool = True,
        despachador_assincrono: DespachadorAssincrono | None = None,
        reportador_de_erros: ReportadorDeErros | None = None,
    ):
        self.uow = uow
        self.event_handlers = event_handlers
        self.command_handlers = command_handlers
        self.subir_erros_de_eventos = subir_erros_de_eventos
        self.despachador_assincrono = despachador_assincrono
        self.reportador_de_erros = reportador_de_erros
        self.queue: list[Mensagem] = []

        self._ambiente_teste = os.getenv("TEST_ENV", "false") == "true"
        self._ambiente_producao = os.getenv("ENV_CONFIG", "development") in [
            "alpha",
            "production",
        ]

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
        """Processa um evento, chamando todos os handlers registrados."""
        if self._deve_despachar_async(event):
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
                self._tratar_erro_evento(erro)

    def _deve_despachar_async(self, event: Evento) -> bool:
        """Verifica se o evento deve ser despachado de forma assíncrona."""
        return (
            isinstance(event, Evento)
            and event.executar_de_forma_assincrona
            and self.despachador_assincrono is not None
        )

    def _tratar_erro_evento(self, erro: Exception) -> None:
        """Trata erro ocorrido durante processamento de evento."""
        if self.subir_erros_de_eventos or self._ambiente_teste:
            raise erro

        if self._ambiente_producao and self.reportador_de_erros:
            self.reportador_de_erros.capturar_excecao(erro)

    async def handle_async_event(self, event: Evento) -> None:
        """Despacha evento para processamento assíncrono."""
        if self.despachador_assincrono is None:
            logger.warning(
                f"Evento {event} marcado como assíncrono mas sem despachador configurado"
            )
            return

        self.despachador_assincrono.despachar(
            evento=event,
            usuario=self.uow.usuario,
        )

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

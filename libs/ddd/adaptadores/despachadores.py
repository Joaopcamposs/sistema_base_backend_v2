"""
Implementações concretas dos protocolos de despacho assíncrono e reportador de erros.

Este módulo contém as implementações específicas que podem ser injetadas
no barramento, permitindo desacoplamento das dependências externas.
"""

from typing import Any

from libs.ddd.barramento import Evento


class DespachadorCelery:
    """Despachador de eventos assíncronos usando Celery.

    Implementa o protocolo DespachadorAssincrono para processar
    eventos de forma assíncrona através do Celery.
    """

    def despachar(self, evento: Evento, usuario: Any) -> None:
        """Despacha evento para processamento pelo Celery."""
        from infra.aplicacoes.celery.tarefas import task_tratar_evento_asyncrono

        tarefa = task_tratar_evento_asyncrono.si(
            evento=evento,
            usuario=usuario,
        )
        tarefa.apply_async()


class ReportadorSentry:
    """Reportador de erros usando Sentry.

    Implementa o protocolo ReportadorDeErros para capturar
    e reportar exceções ao Sentry.
    """

    def capturar_excecao(self, erro: Exception) -> None:
        """Captura e reporta exceção ao Sentry."""
        import sentry_sdk

        sentry_sdk.capture_exception(erro)


class DespachadorNulo:
    """Despachador nulo para testes ou quando não há processamento assíncrono.

    Não faz nada - útil para testes ou ambientes onde não há Celery.
    """

    def despachar(self, evento: Evento, usuario: Any) -> None:
        """Não faz nada - apenas para satisfazer o protocolo."""
        pass


class ReportadorNulo:
    """Reportador nulo para testes ou quando não há reportador configurado.

    Apenas loga o erro - útil para desenvolvimento local.
    """

    def capturar_excecao(self, erro: Exception) -> None:
        """Apenas loga o erro localmente."""
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Erro capturado (sem reportador externo): {erro}")

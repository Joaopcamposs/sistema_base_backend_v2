"""
Testes de integração para o barramento de mensagens.
"""

from dataclasses import dataclass

import pytest

from contextos_de_negocio.dominio.comandos.teste import ComandoTeste
from contextos_de_negocio.dominio.eventos.teste import EventoTeste, EventoTesteAssincrono
from libs.ddd.barramento import (
    Comando,
    Evento,
    BarramentoDeMensagens,
    ManipuladoresDeComandos,
    ManipuladoresDeEventos,
)


class TestBarramentoIntegracao:
    """Testes de integração para o barramento de mensagens."""

    @pytest.fixture
    def mock_uow(self):
        """Cria um mock simples da UoW."""
        from unittest.mock import MagicMock

        uow = MagicMock()
        uow.collect_new_events.return_value = []
        uow.usuario = None
        return uow

    @pytest.mark.asyncio
    async def test_comando_teste_executa_handler(self, mock_uow) -> None:
        """Testa que ComandoTeste executa o handler correto."""
        resultado_capturado = []

        async def handler_teste(comando: ComandoTeste) -> str:
            resultado_capturado.append(comando.mensagem)
            return "ok"

        barramento = BarramentoDeMensagens(
            uow=mock_uow,
            event_handlers={},
            command_handlers=ManipuladoresDeComandos({ComandoTeste: handler_teste}),
        )

        comando = ComandoTeste(mensagem="teste de integração")
        resultado = await barramento.handle(comando)

        assert resultado == "ok"
        assert "teste de integração" in resultado_capturado

    @pytest.mark.asyncio
    async def test_evento_teste_executa_handlers(self, mock_uow) -> None:
        """Testa que EventoTeste executa todos os handlers."""
        handlers_executados = []

        async def handler1(evento: EventoTeste) -> None:
            handlers_executados.append("handler1")

        async def handler2(evento: EventoTeste) -> None:
            handlers_executados.append("handler2")

        barramento = BarramentoDeMensagens(
            uow=mock_uow,
            event_handlers=ManipuladoresDeEventos({EventoTeste: [handler1, handler2]}),
            command_handlers={},
        )

        evento = EventoTeste(mensagem="evento de teste")
        await barramento.handle(evento)

        assert "handler1" in handlers_executados
        assert "handler2" in handlers_executados

    @pytest.mark.asyncio
    async def test_evento_assincrono_com_flag_false(self, mock_uow) -> None:
        """Testa evento assíncrono quando flag está desabilitada."""
        handler_executado = []

        async def handler(evento: EventoTesteAssincrono) -> None:
            handler_executado.append(True)

        barramento = BarramentoDeMensagens(
            uow=mock_uow,
            event_handlers=ManipuladoresDeEventos({EventoTesteAssincrono: [handler]}),
            command_handlers={},
        )

        evento = EventoTesteAssincrono(mensagem="async teste")
        await barramento.handle(evento)

        assert True in handler_executado

    @pytest.mark.asyncio
    async def test_comando_gera_eventos_em_cadeia(self, mock_uow) -> None:
        """Testa que comandos podem gerar eventos em cadeia."""
        execucoes = []

        @dataclass
        class ComandoInicial(Comando):
            valor: int

        @dataclass(kw_only=True)
        class EventoGerado(Evento):
            valor: int

        async def handler_comando(cmd: ComandoInicial) -> str:
            execucoes.append(f"comando:{cmd.valor}")
            return "ok"

        async def handler_evento(evt: EventoGerado) -> None:
            execucoes.append(f"evento:{evt.valor}")

        evento = EventoGerado(valor=42)
        mock_uow.collect_new_events.side_effect = [[evento], []]

        barramento = BarramentoDeMensagens(
            uow=mock_uow,
            event_handlers={EventoGerado: [handler_evento]},
            command_handlers={ComandoInicial: handler_comando},
        )

        await barramento.handle(ComandoInicial(valor=42))

        assert "comando:42" in execucoes
        assert "evento:42" in execucoes

    @pytest.mark.asyncio
    async def test_erro_em_evento_nao_para_outros_handlers(self, mock_uow) -> None:
        """Testa que erro em um handler de evento não para os outros."""

        execucoes = []

        @dataclass(kw_only=True)
        class EventoComErro(Evento):
            pass

        async def handler_com_erro(evt: EventoComErro) -> None:
            raise ValueError("Erro proposital")

        async def handler_ok(evt: EventoComErro) -> None:
            execucoes.append("handler_ok")

        barramento = BarramentoDeMensagens(
            uow=mock_uow,
            event_handlers={EventoComErro: [handler_com_erro, handler_ok]},
            command_handlers={},
            subir_erros_de_eventos=False,
        )
        barramento._ambiente_teste = False

        await barramento.handle(EventoComErro())

        assert "handler_ok" in execucoes

    @pytest.mark.asyncio
    async def test_erro_em_comando_levanta_excecao(self, mock_uow) -> None:
        """Testa que erro em comando levanta exceção."""

        @dataclass
        class ComandoComErro(Comando):
            pass

        async def handler_com_erro(cmd: ComandoComErro) -> None:
            raise ValueError("Erro no comando")

        barramento = BarramentoDeMensagens(
            uow=mock_uow,
            event_handlers={},
            command_handlers={ComandoComErro: handler_com_erro},
        )

        with pytest.raises(ValueError, match="Erro no comando"):
            await barramento.handle(ComandoComErro())


class TestBootstrapIntegracao:
    """Testes de integração para o bootstrap do barramento."""

    @pytest.mark.asyncio
    async def test_inject_dependencies_funciona(self) -> None:
        """Testa que a injeção de dependências funciona corretamente."""
        from libs.ddd.bootstrap import inject_dependencies

        class FakeUoW:
            pass

        uow = FakeUoW()

        async def handler_com_uow(comando, uow):
            return uow

        async def handler_sem_uow(comando):
            return "sem uow"

        injected_with = inject_dependencies(handler_com_uow, {"uow": uow})
        injected_without = inject_dependencies(handler_sem_uow, {"uow": uow})

        @dataclass
        class ComandoFake(Comando):
            pass

        result1 = await injected_with(ComandoFake())
        result2 = await injected_without(ComandoFake())

        assert result1 is uow
        assert result2 == "sem uow"

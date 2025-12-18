"""
Testes unitários para o barramento de mensagens.
"""

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from libs.ddd.barramento import (
    Comando,
    Evento,
    BarramentoDeMensagens,
    CAMPOS_SENSIVEIS,
)


class TestComando:
    """Testes para a classe Comando."""

    def test_criar_comando(self) -> None:
        """Testa criação de comando."""

        @dataclass
        class ComandoTeste(Comando):
            nome: str
            valor: int

        comando = ComandoTeste(nome="teste", valor=42)

        assert comando.nome == "teste"
        assert comando.valor == 42

    def test_comando_repr(self) -> None:
        """Testa representação string do comando."""

        @dataclass
        class ComandoTeste(Comando):
            nome: str

        comando = ComandoTeste(nome="teste")
        repr_str = repr(comando)

        assert "ComandoTeste" in repr_str
        assert "nome='teste'" in repr_str


class TestEvento:
    """Testes para a classe Evento."""

    def test_criar_evento(self) -> None:
        """Testa criação de evento."""

        @dataclass(kw_only=True)
        class EventoTeste(Evento):
            mensagem: str

        evento = EventoTeste(mensagem="algo aconteceu")

        assert evento.mensagem == "algo aconteceu"
        assert evento.executar_de_forma_assincrona is False

    def test_evento_assincrono(self) -> None:
        """Testa evento com flag assíncrona."""

        @dataclass(kw_only=True)
        class EventoAssincrono(Evento):
            mensagem: str

        evento = EventoAssincrono(
            mensagem="evento async",
            executar_de_forma_assincrona=True,
        )

        assert evento.executar_de_forma_assincrona is True


class TestBaseComandoOuEvento:
    """Testes para a classe BaseComandoOuEvento."""

    def test_censura_campo_senha(self) -> None:
        """Testa que campo senha é censurado no repr."""

        @dataclass
        class ComandoComSenha(Comando):
            usuario: str
            senha: str

        comando = ComandoComSenha(usuario="joao", senha="123456")
        repr_str = repr(comando)

        assert "senha='***'" in repr_str
        assert "123456" not in repr_str

    def test_censura_campo_token(self) -> None:
        """Testa que campo token é censurado no repr."""

        @dataclass
        class ComandoComToken(Comando):
            usuario: str
            token: str

        comando = ComandoComToken(usuario="joao", token="abc123xyz")
        repr_str = repr(comando)

        assert "token='***'" in repr_str
        assert "abc123xyz" not in repr_str

    def test_campos_sensiveis(self) -> None:
        """Testa que campos sensíveis estão definidos."""
        assert "senha" in CAMPOS_SENSIVEIS
        assert "token" in CAMPOS_SENSIVEIS


class TestBarramentoDeMensagens:
    """Testes para a classe BarramentoDeMensagens."""

    @pytest.fixture
    def mock_uow(self) -> MagicMock:
        """Cria um mock da UnidadeDeTrabalho."""
        uow = MagicMock()
        uow.collect_new_events.return_value = []
        return uow

    @pytest.mark.asyncio
    async def test_handle_comando(self, mock_uow: MagicMock) -> None:
        """Testa processamento de comando."""

        @dataclass
        class ComandoTeste(Comando):
            valor: int

        handler_chamado = False
        resultado_esperado = "sucesso"

        async def handler(cmd: ComandoTeste) -> str:
            nonlocal handler_chamado
            handler_chamado = True
            return resultado_esperado

        barramento = BarramentoDeMensagens(
            uow=mock_uow,
            event_handlers={},
            command_handlers={ComandoTeste: handler},
        )

        comando = ComandoTeste(valor=42)
        resultado = await barramento.handle(comando)

        assert handler_chamado is True
        assert resultado == resultado_esperado

    @pytest.mark.asyncio
    async def test_handle_evento(self, mock_uow: MagicMock) -> None:
        """Testa processamento de evento."""

        @dataclass(kw_only=True)
        class EventoTeste(Evento):
            mensagem: str

        handlers_chamados = []

        async def handler1(evt: EventoTeste) -> None:
            handlers_chamados.append("handler1")

        async def handler2(evt: EventoTeste) -> None:
            handlers_chamados.append("handler2")

        barramento = BarramentoDeMensagens(
            uow=mock_uow,
            event_handlers={EventoTeste: [handler1, handler2]},
            command_handlers={},
        )

        evento = EventoTeste(mensagem="teste")
        await barramento.handle(evento)

        assert "handler1" in handlers_chamados
        assert "handler2" in handlers_chamados

    @pytest.mark.asyncio
    async def test_handle_comando_gera_evento(self, mock_uow: MagicMock) -> None:
        """Testa que comando pode gerar eventos."""

        @dataclass
        class ComandoTeste(Comando):
            pass

        @dataclass(kw_only=True)
        class EventoGerado(Evento):
            pass

        evento_processado = False

        async def command_handler(cmd: ComandoTeste) -> None:
            pass

        async def event_handler(evt: EventoGerado) -> None:
            nonlocal evento_processado
            evento_processado = True

        evento = EventoGerado()
        mock_uow.collect_new_events.side_effect = [
            [evento],
            [],
        ]

        barramento = BarramentoDeMensagens(
            uow=mock_uow,
            event_handlers={EventoGerado: [event_handler]},
            command_handlers={ComandoTeste: command_handler},
        )

        await barramento.handle(ComandoTeste())

        assert evento_processado is True

    @pytest.mark.asyncio
    async def test_handle_comando_inexistente_levanta_erro(
        self, mock_uow: MagicMock
    ) -> None:
        """Testa que comando sem handler levanta erro."""

        @dataclass
        class ComandoSemHandler(Comando):
            pass

        barramento = BarramentoDeMensagens(
            uow=mock_uow,
            event_handlers={},
            command_handlers={},
        )

        with pytest.raises(KeyError):
            await barramento.handle(ComandoSemHandler())

    @pytest.mark.asyncio
    async def test_evento_sem_handler_nao_levanta_erro(self, mock_uow: MagicMock) -> None:
        """Testa que evento sem handler não levanta erro."""

        @dataclass(kw_only=True)
        class EventoSemHandler(Evento):
            pass

        barramento = BarramentoDeMensagens(
            uow=mock_uow,
            event_handlers={},
            command_handlers={},
        )

        await barramento.handle(EventoSemHandler())

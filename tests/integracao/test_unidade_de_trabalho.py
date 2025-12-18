"""
Testes de integração para a Unidade de Trabalho.
"""

from uuid import uuid4

import pytest

from contextos_de_negocio.dominio.entidades.usuario import Usuario
from libs.ddd.unidade_de_trabalho import (
    UnidadeDeTrabalhoSchemaComProblema,
)
from libs.utils.tipos_basicos import Email, CPF


class TestUnidadeDeTrabalhoAbstrata:
    """Testes para UnidadeDeTrabalhoAbstrata."""

    def test_uow_requer_usuario(self) -> None:
        """Testa que UoW requer usuário."""
        from libs.ddd.unidade_de_trabalho import UnidadeDeTrabalhoBase

        with pytest.raises((UnidadeDeTrabalhoSchemaComProblema, AttributeError)):
            UnidadeDeTrabalhoBase(
                session_factory=lambda: None,
                engine_factory=lambda: None,
                base=None,
                usuario=None,
            )

    def test_uow_schema_diferente_de_empresa_levanta_erro(self) -> None:
        """Testa que schema diferente da empresa do usuário levanta erro."""
        from libs.ddd.unidade_de_trabalho import UnidadeDeTrabalhoBase

        empresa_id = uuid4()
        outro_schema = str(uuid4())

        usuario = Usuario(
            id=uuid4(),
            empresa=empresa_id,
            nome="Teste",
            email=Email("teste@teste.com"),
            cpf=CPF(CPF.gerar()),
            ativo=True,
            adm=False,
            _senha="hash",
            permissoes=[],
        )

        with pytest.raises(UnidadeDeTrabalhoSchemaComProblema):
            UnidadeDeTrabalhoBase(
                session_factory=lambda: None,
                engine_factory=lambda: None,
                base=None,
                usuario=usuario,
                schema=outro_schema,
            )

    def test_uow_schema_igual_empresa_nao_levanta_erro(self) -> None:
        """Testa que schema igual à empresa do usuário não levanta erro."""
        from libs.ddd.unidade_de_trabalho import UnidadeDeTrabalhoBase

        empresa_id = uuid4()

        usuario = Usuario(
            id=uuid4(),
            empresa=empresa_id,
            nome="Teste",
            email=Email("teste@teste.com"),
            cpf=CPF(CPF.gerar()),
            ativo=True,
            adm=False,
            _senha="hash",
            permissoes=[],
        )

        uow = UnidadeDeTrabalhoBase(
            session_factory=lambda: None,
            engine_factory=lambda: None,
            base=None,
            usuario=usuario,
            schema=str(empresa_id),
        )

        assert uow.schema == str(empresa_id)


class TestUnidadeDeTrabalhoEventos:
    """Testes para coleta de eventos na UoW."""

    def test_adicionar_evento_fora_de_agregado(self) -> None:
        """Testa adição de evento fora de agregado."""
        from libs.ddd.unidade_de_trabalho import UnidadeDeTrabalhoBase
        from libs.ddd.barramento import Evento
        from dataclasses import dataclass

        @dataclass(kw_only=True)
        class EventoTeste(Evento):
            valor: int

        empresa_id = uuid4()
        usuario = Usuario(
            id=uuid4(),
            empresa=empresa_id,
            nome="Teste",
            email=Email("teste@teste.com"),
            cpf=CPF(CPF.gerar()),
            ativo=True,
            adm=False,
            _senha="hash",
            permissoes=[],
        )

        uow = UnidadeDeTrabalhoBase(
            session_factory=lambda: None,
            engine_factory=lambda: None,
            base=None,
            usuario=usuario,
        )

        evento = EventoTeste(valor=42)
        uow.adicionar_evento_fora_de_agregado(evento)

        assert evento in uow.eventos_fora_de_agregado

    def test_collect_new_events_de_agregado(self) -> None:
        """Testa coleta de eventos de agregados."""
        from libs.ddd.unidade_de_trabalho import UnidadeDeTrabalhoBase
        from libs.ddd.barramento import Evento
        from dataclasses import dataclass
        from unittest.mock import MagicMock

        @dataclass(kw_only=True)
        class EventoTeste(Evento):
            valor: int

        empresa_id = uuid4()
        usuario = Usuario(
            id=uuid4(),
            empresa=empresa_id,
            nome="Teste",
            email=Email("teste@teste.com"),
            cpf=CPF(CPF.gerar()),
            ativo=True,
            adm=False,
            _senha="hash",
            permissoes=[],
        )

        uow = UnidadeDeTrabalhoBase(
            session_factory=lambda: None,
            engine_factory=lambda: None,
            base=None,
            usuario=usuario,
        )

        evento = EventoTeste(valor=123)

        mock_agregado = MagicMock()
        mock_agregado.eventos = [evento]

        mock_repo = MagicMock()
        mock_repo.seen = {mock_agregado}
        uow.domain_repo = mock_repo

        eventos = list(uow.collect_new_events())

        assert len(eventos) == 1
        assert eventos[0].valor == 123

    def test_empresa_property(self) -> None:
        """Testa property empresa da UoW."""
        from libs.ddd.unidade_de_trabalho import UnidadeDeTrabalhoBase

        empresa_id = uuid4()
        usuario = Usuario(
            id=uuid4(),
            empresa=empresa_id,
            nome="Teste",
            email=Email("teste@teste.com"),
            cpf=CPF(CPF.gerar()),
            ativo=True,
            adm=False,
            _senha="hash",
            permissoes=[],
        )

        uow = UnidadeDeTrabalhoBase(
            session_factory=lambda: None,
            engine_factory=lambda: None,
            base=None,
            usuario=usuario,
        )

        assert uow.empresa == empresa_id

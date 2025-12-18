"""
Testes de integração para o repositório de usuário.
"""

from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from contextos_de_negocio.adaptadores.orm.declarativo.usuario import UsuarioDB
from contextos_de_negocio.adaptadores.repositorio.repo_dominio.usuario import (
    UsuarioRepoDominio,
)
from contextos_de_negocio.adaptadores.repositorio.repo_consulta.usuario import (
    UsuarioRepoConsulta,
)
from contextos_de_negocio.dominio.agregados.usuario import Usuario
from contextos_de_negocio.dominio.excecoes import (
    UsuarioJaCadastrado,
    UsuarioNaoEncontrado,
)
from libs.ddd.visualizadores.filtro import Filtros
from libs.utils.tipos_basicos import Email, CPF


class TestUsuarioRepoDominio:
    """Testes de integração para UsuarioRepoDominio."""

    @pytest_asyncio.fixture
    async def repo_dominio(self, test_session: AsyncSession) -> UsuarioRepoDominio:
        """Cria repositório de domínio com sessão de teste."""
        return UsuarioRepoDominio(session=test_session)

    @pytest_asyncio.fixture
    async def empresa_id(self, test_session: AsyncSession, test_schema: str) -> str:
        """Cria uma empresa de teste e retorna seu ID."""
        from contextos_de_negocio.adaptadores.orm.declarativo.empresa import EmpresaDB

        empresa_id = uuid4()
        empresa = EmpresaDB(
            id=empresa_id,
            razao_social="Empresa Teste LTDA",
            nome_fantasia="Empresa Teste",
            nome_responsavel="João",
            email="empresa@teste.com",
            cpf="46865954874",
            cnpj="12345678000190",
            ativo=True,
        )
        test_session.add(empresa)
        await test_session.commit()
        return str(empresa_id)

    @pytest.mark.asyncio
    async def test_gerar_agregado_para_cadastro(
        self, repo_dominio: UsuarioRepoDominio, empresa_id: str
    ) -> None:
        """Testa geração de agregado para cadastro."""
        usuario = await repo_dominio.gerar_agregado_para_cadastro(
            empresa=uuid4().hex if not empresa_id else empresa_id,
            nome="João Teste",
            email="joao@teste.com",
            cpf=CPF.gerar(),
            senha="senha123",
            ativo=True,
            adm=False,
            permissoes=[],
        )

        assert usuario is not None
        assert usuario.nome == "João Teste"
        assert usuario.email == "joao@teste.com"

    @pytest.mark.asyncio
    async def test_gerar_agregado_email_duplicado_levanta_erro(
        self,
        repo_dominio: UsuarioRepoDominio,
        test_session: AsyncSession,
        empresa_id: str,
    ) -> None:
        """Testa que email duplicado levanta UsuarioJaCadastrado."""
        cpf = CPF.gerar()
        usuario_db = UsuarioDB(
            id=uuid4(),
            empresa_id=empresa_id,
            nome="Existente",
            email="existente@teste.com",
            cpf=cpf,
            senha_hash="hash",
            ativo=True,
            adm=False,
            permissoes=[],
        )
        test_session.add(usuario_db)
        await test_session.commit()

        with pytest.raises(UsuarioJaCadastrado):
            await repo_dominio.gerar_agregado_para_cadastro(
                empresa=empresa_id,
                nome="Novo",
                email="existente@teste.com",
                cpf=CPF.gerar(),
                senha="senha",
                ativo=True,
                adm=False,
                permissoes=[],
            )

    @pytest.mark.asyncio
    async def test_adicionar_usuario(
        self,
        repo_dominio: UsuarioRepoDominio,
        test_session: AsyncSession,
        empresa_id: str,
    ) -> None:
        """Testa adição de usuário no banco."""
        usuario = Usuario.retornar_agregado_para_cadastro(
            empresa=empresa_id,
            nome="Novo Usuario",
            email=Email("novo@teste.com"),
            cpf=CPF(CPF.gerar()),
            senha="senha123",
            ativo=True,
            adm=False,
            permissoes=[],
        )
        usuario.cadastrar(id_usuario=uuid4())

        await repo_dominio.adicionar(usuario)
        await test_session.commit()

        result = await test_session.execute(
            text(f"SELECT * FROM usuario WHERE id = '{usuario.id}'")
        )
        row = result.fetchone()

        assert row is not None
        assert row.nome == "Novo Usuario"

    @pytest.mark.asyncio
    async def test_consultar_um_por_filtros(
        self,
        repo_dominio: UsuarioRepoDominio,
        test_session: AsyncSession,
        empresa_id: str,
    ) -> None:
        """Testa consulta de usuário por filtros."""
        cpf = CPF.gerar()
        usuario_db = UsuarioDB(
            id=uuid4(),
            empresa_id=empresa_id,
            nome="Para Consulta",
            email="consulta@teste.com",
            cpf=cpf,
            senha_hash="hash",
            ativo=True,
            adm=False,
            permissoes=[],
        )
        test_session.add(usuario_db)
        await test_session.commit()

        filtros = Filtros({"email": "consulta@teste.com"})
        usuario = await repo_dominio.consultar_um_por_filtros(filtros=filtros)

        assert usuario is not None
        assert usuario.email == "consulta@teste.com"
        assert usuario.nome == "Para Consulta"

    @pytest.mark.asyncio
    async def test_consultar_usuario_inexistente_levanta_erro(
        self, repo_dominio: UsuarioRepoDominio
    ) -> None:
        """Testa que consulta de usuário inexistente levanta erro."""
        filtros = Filtros({"email": "naoexiste@teste.com"})

        with pytest.raises(UsuarioNaoEncontrado):
            await repo_dominio.consultar_um_por_filtros(filtros=filtros)


class TestUsuarioRepoConsulta:
    """Testes de integração para UsuarioRepoConsulta."""

    @pytest_asyncio.fixture
    async def repo_consulta(self, test_session: AsyncSession) -> UsuarioRepoConsulta:
        """Cria repositório de consulta com sessão de teste."""
        return UsuarioRepoConsulta(session=test_session)

    @pytest_asyncio.fixture
    async def empresa_id(self, test_session: AsyncSession) -> str:
        """Cria uma empresa de teste e retorna seu ID."""
        from contextos_de_negocio.adaptadores.orm.declarativo.empresa import EmpresaDB

        empresa_id = uuid4()
        empresa = EmpresaDB(
            id=empresa_id,
            razao_social="Empresa Consulta LTDA",
            nome_fantasia="Empresa Consulta",
            nome_responsavel="Maria",
            email="empresa.consulta@teste.com",
            cpf="46865954874",
            cnpj="98765432000190",
            ativo=True,
        )
        test_session.add(empresa)
        await test_session.commit()
        return str(empresa_id)

    @pytest.mark.asyncio
    async def test_consultar_um_por_email(
        self,
        repo_consulta: UsuarioRepoConsulta,
        test_session: AsyncSession,
        empresa_id: str,
    ) -> None:
        """Testa consulta de usuário por email."""
        cpf = CPF.gerar()
        usuario_db = UsuarioDB(
            id=uuid4(),
            empresa_id=empresa_id,
            nome="Usuario Email",
            email="email.consulta@teste.com",
            cpf=cpf,
            senha_hash="hash",
            ativo=True,
            adm=False,
            permissoes=[],
        )
        test_session.add(usuario_db)
        await test_session.commit()

        usuario = await repo_consulta.consultar_um_por_email("email.consulta@teste.com")

        assert usuario is not None
        assert usuario.email == "email.consulta@teste.com"

    @pytest.mark.asyncio
    async def test_consultar_email_inexistente_retorna_none(
        self, repo_consulta: UsuarioRepoConsulta
    ) -> None:
        """Testa que email inexistente retorna None."""
        usuario = await repo_consulta.consultar_um_por_email("naoexiste@teste.com")

        assert usuario is None

    @pytest.mark.asyncio
    async def test_consultar_por_filtros_multiplos(
        self,
        repo_consulta: UsuarioRepoConsulta,
        test_session: AsyncSession,
        empresa_id: str,
    ) -> None:
        """Testa consulta com múltiplos filtros."""
        for i in range(3):
            usuario_db = UsuarioDB(
                id=uuid4(),
                empresa_id=empresa_id,
                nome=f"Usuario {i}",
                email=f"usuario{i}@filtro.com",
                cpf=CPF.gerar(),
                senha_hash="hash",
                ativo=True,
                adm=False,
                permissoes=[],
            )
            test_session.add(usuario_db)
        await test_session.commit()

        filtros = Filtros({"ativo": True})
        usuarios = await repo_consulta.consultar_por_filtros(filtros=filtros)

        assert len(usuarios) >= 3

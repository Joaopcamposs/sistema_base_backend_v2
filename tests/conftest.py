"""
Configurações de testes para o projeto sistema_base_backend_v2.
Contém fixtures compartilhadas entre testes unitários e de integração.
"""

from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine

os.environ["TEST_ENV"] = "true"

from contextos_de_negocio.dominio.entidades.usuario import Usuario
from libs.ddd.adaptadores.orm import Base
from libs.utils.tipos_basicos import Email, CPF


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Cria um event loop para toda a sessão de testes."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db_uri() -> str:
    """Retorna a URI do banco de dados de teste."""
    em_docker = os.getenv("IN_DOCKER", "false").lower() == "true"
    host = "postgres_test" if em_docker else "localhost"
    port = 5432
    return f"postgresql+asyncpg://postgres:password@{host}:{port}/postgres"


@pytest_asyncio.fixture(scope="session")
async def test_engine(test_db_uri: str) -> AsyncGenerator[AsyncEngine, None]:
    """Cria uma engine de teste para toda a sessão."""
    engine = create_async_engine(test_db_uri, isolation_level="READ COMMITTED")
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_schema(test_engine: AsyncEngine) -> AsyncGenerator[str, None]:
    """Cria um schema único para cada teste e limpa após o teste."""
    schema_name = f"test_{uuid4().hex[:8]}"

    async with test_engine.begin() as conn:
        await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))

        for table in Base.metadata.sorted_tables:
            if table.schema == "public":
                continue
            table.schema = schema_name

        await conn.run_sync(Base.metadata.create_all)

        for table in Base.metadata.sorted_tables:
            if table.schema == schema_name:
                table.schema = None

    yield schema_name

    async with test_engine.begin() as conn:
        await conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))


@pytest_asyncio.fixture(scope="function")
async def test_session(
    test_engine: AsyncEngine, test_schema: str
) -> AsyncGenerator[AsyncSession, None]:
    """Cria uma sessão de teste com schema isolado."""
    execution_options = {"schema_translate_map": {None: test_schema}}

    session = AsyncSession(
        bind=test_engine.execution_options(**execution_options),
        autoflush=True,
        expire_on_commit=False,
    )
    await session.execute(text(f'SET search_path TO "{test_schema}"'))

    yield session

    await session.rollback()
    await session.close()


@pytest.fixture
def usuario_teste() -> Usuario:
    """Retorna um usuário de teste válido."""
    empresa_id = uuid4()
    return Usuario(
        id=uuid4(),
        empresa=empresa_id,
        nome="Usuário Teste",
        email=Email("teste@teste.com"),
        cpf=CPF(CPF.gerar()),
        ativo=True,
        adm=False,
        _senha="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.V5yT5Q5Q5Q5Q5Q",
        permissoes=[],
    )


@pytest.fixture
def empresa_id() -> str:
    """Retorna um ID de empresa de teste."""
    return str(uuid4())

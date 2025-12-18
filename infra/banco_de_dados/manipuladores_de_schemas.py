from typing import Callable

from sqlalchemy import text, Sequence
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, AsyncConnection
from sqlalchemy.orm import DeclarativeBase


async def verificar_schema_existente(conn: AsyncConnection, schema_id: str) -> None:
    result = await conn.execute(
        text(
            f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{schema_id}'"
        )
    )
    if result.fetchone():
        raise ValueError(f"Schema {schema_id} já existe")


async def criar_schema_e_tabelas(
    engine_factory: Callable, base: type[DeclarativeBase], schema_id: str
) -> None:
    """
    1. Cria o schema no Postgres
    2. Ajusta os metadados para usar schema_id
    3. Cria as tabelas do tenant dentro dele
    4. Restaura schema=None nos metadados
    """
    # criar engine temporária
    engine_temp: AsyncEngine = engine_factory(force_create_engine=True)

    try:
        # 1) criar schema
        async with engine_temp.begin() as conn:
            await verificar_schema_existente(conn, schema_id)
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_id}"'))

        # 2) atribuir schema nos objetos
        for table in base.metadata.sorted_tables:
            if table.schema == "public":
                continue
            table.schema = schema_id
            for column in table.columns:
                if isinstance(column.default, Sequence):
                    column.default.schema = schema_id

        # 3) criar tabelas no novo schema
        async with engine_temp.begin() as conn:
            await conn.run_sync(base.metadata.create_all)

        # 4) restaurar esquema padrão (public)
        for table in base.metadata.sorted_tables:
            if table.schema == schema_id:
                table.schema = None
    finally:
        await engine_temp.dispose()


async def criar_schema_completo_dentro_de_uma_transacao(
    engine_factory: Callable,
    base: type[DeclarativeBase],
    session_factory: Callable,
    schema_id: str | None,
) -> AsyncSession:
    await criar_schema_e_tabelas(
        engine_factory=engine_factory, base=base, schema_id=schema_id
    )

    if schema_id:
        schema_id = str(schema_id)

    session = await session_factory(
        somente_leitura=False, schema=schema_id, force_create_engine=True
    )

    return session

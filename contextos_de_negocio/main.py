from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from fastapi import FastAPI

from contextos_de_negocio.pontos_de_entrada.api_publica.empresa import (
    router_empresa,
)
from contextos_de_negocio.pontos_de_entrada.api_publica.seguranca import (
    router_seguranca,
)
from contextos_de_negocio.pontos_de_entrada.api_publica.teste import router_teste
from contextos_de_negocio.pontos_de_entrada.api_publica.usuario import (
    router_usuario,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    from infra.banco_de_dados.inicializadores import criar_primeira_empresa_e_usuario

    await criar_primeira_empresa_e_usuario()
    yield


app = FastAPI(
    title="API Sistema Base Backend",
    description="APIs REST",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)


@app.get("/")
async def test() -> dict[str, str]:
    return {"message": "API está no ar!"}


app.include_router(router_seguranca)
app.include_router(router_teste)
app.include_router(router_empresa)
app.include_router(router_usuario)

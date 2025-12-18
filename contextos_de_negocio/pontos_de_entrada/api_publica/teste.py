from http import HTTPStatus

from fastapi import APIRouter
from starlette.responses import JSONResponse

from contextos_de_negocio.barramento.bootstrap import bootstrap
from contextos_de_negocio.dominio.comandos.teste import ComandoTeste

router_teste = APIRouter(prefix="/api/v1", tags=["Teste"])


@router_teste.post("/comando_teste")
async def comando_teste_api(
    mensagem: str,
) -> JSONResponse:
    from infra.banco_de_dados.inicializadores import gerar_usuario_fake_primeiro_cadastro
    from uuid import uuid4

    usuario = gerar_usuario_fake_primeiro_cadastro(uuid4())

    bus = bootstrap(usuario=usuario)

    comando = ComandoTeste(mensagem)
    retorno = await bus.handle(comando)

    return JSONResponse(status_code=HTTPStatus.OK, content=str(retorno))

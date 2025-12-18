from http import HTTPStatus

from fastapi import APIRouter, Depends
from pydantic import UUID4
from starlette.responses import JSONResponse

from contextos_de_negocio.adaptadores.visualizadores.usuario import (
    listar_usuarios_por_id_e_email,
)
from contextos_de_negocio.dominio.comandos.usuario import (
    CadastrarUsuario,
    AtualizarUsuario,
    RemoverUsuario,
)
from contextos_de_negocio.dominio.entidades.usuario import Usuario
from contextos_de_negocio.dominio.excecoes import UsuarioNaoEncontrado
from contextos_de_negocio.pontos_de_entrada.schemas.usuario import (
    CadastrarUsuarioSchema,
    LerUsuarioSchema,
    AtualizarUsuarioSchema,
)
from contextos_de_negocio.servicos.executores.seguranca import (
    current_user,
    get_current_user,
)

router_usuario = APIRouter(
    prefix="/api/v1", tags=["Usuários"], dependencies=[Depends(get_current_user)]
)


@router_usuario.get("/usuarios", response_model=list[LerUsuarioSchema])
async def listar(id: UUID4 | None = None, email: str | None = None) -> list[Usuario]:
    unidade_de_trabalho: UnidadeDeTrabalho = UnidadeDeTrabalho(usuario=current_user.get())

    usuarios = await listar_usuarios_por_id_e_email(
        unidade_de_trabalho=unidade_de_trabalho, id=id, email=email
    )

    if not usuarios:
        raise UsuarioNaoEncontrado

    return usuarios


@router_usuario.post("/usuario")
async def cadastrar(
    novo_usuario: CadastrarUsuarioSchema,
) -> JSONResponse:
    bus = bootstrap(usuario=current_user.get())

    comando = CadastrarUsuario(**novo_usuario.__dict__)
    retorno = await bus.handle(comando)

    return JSONResponse(status_code=HTTPStatus.CREATED, content=str(retorno))


@router_usuario.put("/usuario", response_model=LerUsuarioSchema)
async def atualizar(
    usuario_atualizado: AtualizarUsuarioSchema,
    id: UUID4 | None = None,
    email: str | None = None,
) -> JSONResponse:
    bus = bootstrap(usuario=current_user.get())

    comando = AtualizarUsuario(**usuario_atualizado.__dict__, id=id, email_antigo=email)
    retorno = await bus.handle(comando)

    return JSONResponse(status_code=HTTPStatus.OK, content=str(retorno))


@router_usuario.delete("/usuario")
async def remover(id: UUID4 | None = None, email: str | None = None) -> JSONResponse:
    bus = bootstrap(usuario=current_user.get())

    comando = RemoverUsuario(id=id, email=email)
    retorno = await bus.handle(comando)

    return JSONResponse(status_code=HTTPStatus.OK, content=str(retorno))

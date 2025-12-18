from http import HTTPStatus
from uuid import uuid4

from fastapi import APIRouter, Depends
from pydantic import UUID4
from starlette.responses import JSONResponse

from contextos_de_negocio.adaptadores.visualizadores.empresa import listar_empresas_por_id
from contextos_de_negocio.barramento.bootstrap import bootstrap
from contextos_de_negocio.barramento.unidade_de_trabalho import UnidadeDeTrabalho
from contextos_de_negocio.dominio.comandos.empresa import (
    CadastrarEmpresa,
    AtualizarEmpresa,
    RemoverEmpresa,
)
from contextos_de_negocio.dominio.entidades.empresa import Empresa
from contextos_de_negocio.dominio.excecoes import EmpresaNaoEncontrada
from contextos_de_negocio.pontos_de_entrada.schemas.empresa import (
    LerEmpresaSchema,
    CadastrarEmpresaSchema,
    AtualizarEmpresaSchema,
)
from contextos_de_negocio.servicos.executores.seguranca import (
    get_current_user,
    current_user,
)
from libs.utils.constantes import CHAVE_SECRETA
from libs.utils.tipos_basicos import CPF, Email, CNPJ

router_empresa = APIRouter(
    prefix="/api/v1", tags=["Empresas"], dependencies=[Depends(get_current_user)]
)


@router_empresa.get("/empresas", response_model=list[LerEmpresaSchema])
async def listar(id: UUID4 | None = None) -> list[Empresa]:
    unidade_de_trabalho: UnidadeDeTrabalho = UnidadeDeTrabalho(usuario=current_user.get())

    empresas = await listar_empresas_por_id(
        unidade_de_trabalho=unidade_de_trabalho, id=id
    )

    if not empresas:
        raise EmpresaNaoEncontrada

    return empresas


@router_empresa.post("/empresa")
async def cadastrar(
    novo_empresa: CadastrarEmpresaSchema,
) -> JSONResponse:
    if novo_empresa.chave_secreta != CHAVE_SECRETA:
        raise ValueError("Chave secreta inválida")

    id_empresa = uuid4()

    bus = bootstrap(
        usuario=current_user.get(),
        schema=str(id_empresa),
        criar_schema=True,
    )

    comando = CadastrarEmpresa(
        razao_social=novo_empresa.razao_social,
        nome_responsavel=novo_empresa.nome_responsavel,
        ativo=novo_empresa.ativo,
        cpf=CPF(novo_empresa.cpf),
        email=Email(novo_empresa.email),
        senha=novo_empresa.senha,
        cnpj=CNPJ(novo_empresa.cnpj),
        nome_fantasia=novo_empresa.nome_fantasia,
        id=id_empresa,
        deve_criar_usuario=novo_empresa.deve_criar_usuario,
    )
    retorno = await bus.handle(comando)

    return JSONResponse(status_code=HTTPStatus.CREATED, content=str(retorno))


@router_empresa.put("/empresa", response_model=LerEmpresaSchema)
async def atualizar(
    empresa_atualizado: AtualizarEmpresaSchema,
    id: UUID4 | None = None,
    email: str | None = None,
) -> JSONResponse:
    bus = bootstrap(usuario=current_user.get())

    comando = AtualizarEmpresa(**empresa_atualizado.__dict__, id=id, email_antigo=email)
    retorno = await bus.handle(comando)

    return JSONResponse(status_code=HTTPStatus.OK, content=str(retorno))


@router_empresa.delete("/empresa")
async def remover(
    id: UUID4 | None = None,
    email: str | None = None,
) -> JSONResponse:
    bus = bootstrap(usuario=current_user.get())

    comando = RemoverEmpresa(id=id, email=email)
    retorno = await bus.handle(comando)

    return JSONResponse(status_code=HTTPStatus.OK, content=str(retorno))

from uuid import UUID

from contextos_de_negocio.dominio.comandos.empresa import (
    CadastrarEmpresa,
    AtualizarEmpresa,
    RemoverEmpresa,
)
from infra.banco_de_dados import validar_email_da_empresa, excluir_schema
from libs.ddd.visualizadores.filtro import Filtros
from libs.utils.tipos_basicos import Email


async def cadastrar_empresa(
    comando: CadastrarEmpresa, unidade_de_trabalho: UnidadeDeTrabalho
) -> UUID:
    from contextos_de_negocio import Dominio, EmpresaRepoDominio

    try:
        async with unidade_de_trabalho(Dominio.empresa) as uow:
            repo_dominio: EmpresaRepoDominio = uow.domain_repo

            await validar_email_da_empresa(comando.email)

            nova_empresa = await repo_dominio.gerar_agregado_para_cadastro(
                razao_social=comando.razao_social,
                nome_fantasia=comando.nome_fantasia,
                nome_responsavel=comando.nome_responsavel,
                email=comando.email,
                cpf=comando.cpf,
                cnpj=comando.cnpj,
                ativo=comando.ativo,
                id=comando.id,
                _eh_primeira_empresa=comando._eh_primeira_empresa,
            )
            nova_empresa.cadastrar(usuario=uow.usuario, senha=comando.senha)

            await repo_dominio.adicionar(
                empresa=nova_empresa,
            )
            await uow.commit()

        return nova_empresa.id
    except Exception as erro:
        await excluir_schema(str(comando.id))
        print(f"Erro ao criar empresa. O schema {str(comando.id)} foi dropado", erro)
        raise erro


async def atualizar_empresa(
    comando: AtualizarEmpresa, unidade_de_trabalho: UnidadeDeTrabalho
) -> UUID:
    from contextos_de_negocio import Dominio, EmpresaRepoDominio

    async with unidade_de_trabalho(Dominio.empresa) as uow:
        repo_dominio: EmpresaRepoDominio = uow.domain_repo

        filtros = Filtros(
            {
                "id": comando.id,
                "email": Email(comando.email_antigo),
            }
        )
        empresa = await repo_dominio.consultar_um_por_filtros(filtros=filtros)
        empresa.atualizar(
            razao_social=comando.razao_social,
            nome_fantasia=comando.nome_fantasia,
            nome_responsavel=comando.nome_responsavel,
            email=comando.email,
            cpf=comando.cpf,
            cnpj=comando.cnpj,
            ativo=comando.ativo,
            usuario=uow.usuario,
        )

        await repo_dominio.adicionar(
            empresa=empresa,
        )
        await uow.commit()

    return empresa.id


async def remover_empresa(
    comando: RemoverEmpresa, unidade_de_trabalho: UnidadeDeTrabalho
) -> UUID:
    from contextos_de_negocio import Dominio, EmpresaRepoDominio

    async with unidade_de_trabalho(Dominio.usuario) as uow:
        repo_dominio: EmpresaRepoDominio = uow.domain_repo

        filtros = Filtros(
            {
                "id": comando.id,
                "email": Email(comando.email),
            }
        )
        empresa = await repo_dominio.consultar_um_por_filtros(filtros=filtros)
        empresa.remover(usuario=uow.usuario)

        await repo_dominio.remover(
            empresa=empresa,
        )
        await uow.commit()

    return empresa.id

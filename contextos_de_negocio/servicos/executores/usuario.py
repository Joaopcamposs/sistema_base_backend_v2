from uuid import UUID

from contextos_de_negocio.dominio.agregados.usuario import UsuarioPublico
from contextos_de_negocio.dominio.comandos.usuario import (
    CadastrarUsuario,
    AtualizarUsuario,
    RemoverUsuario,
)
from contextos_de_negocio.dominio.eventos.usuario import (
    UsuarioCriado,
    ChegouAHoraDeCriarUsuarioInicialDaEmpresa,
    ChegouAHoraDeCriarUsuarioADMDaEmpresa,
    UsuarioAtualizado,
    UsuarioRemovido,
)
from libs.ddd.visualizadores.filtro import Filtros


async def cadastrar_usuario(
    comando_ou_evento: CadastrarUsuario
    | ChegouAHoraDeCriarUsuarioInicialDaEmpresa
    | ChegouAHoraDeCriarUsuarioADMDaEmpresa,
    unidade_de_trabalho: UnidadeDeTrabalho,
) -> UUID:
    from contextos_de_negocio import Dominio, UsuarioRepoDominio

    async with unidade_de_trabalho(Dominio.usuario) as uow:
        repo_dominio: UsuarioRepoDominio = uow.domain_repo

        novo_usuario = await repo_dominio.gerar_agregado_para_cadastro(
            empresa=comando_ou_evento.empresa,
            nome=comando_ou_evento.nome,
            email=comando_ou_evento.email,
            cpf=comando_ou_evento.cpf,
            senha=comando_ou_evento.senha,
            adm=comando_ou_evento.adm,
            ativo=comando_ou_evento.ativo,
            permissoes=comando_ou_evento.permissoes,
        )
        novo_usuario.cadastrar(
            usuario=uow.usuario,
        )

        await repo_dominio.adicionar(
            usuario=novo_usuario,
        )
        await uow.commit()

    return novo_usuario.id


async def atualizar_usuario(
    comando: AtualizarUsuario, unidade_de_trabalho: UnidadeDeTrabalho
) -> UUID:
    from contextos_de_negocio import Dominio, UsuarioRepoDominio

    async with unidade_de_trabalho(Dominio.usuario) as uow:
        repo_dominio: UsuarioRepoDominio = uow.domain_repo

        filtros = Filtros(
            {
                "id": comando.id,
                "email": comando.email_antigo,
            }
        )
        usuario = await repo_dominio.consultar_um_por_filtros(filtros=filtros)
        usuario.atualizar(
            nome=comando.nome,
            email=comando.email,
            cpf=comando.cpf,
            senha=comando.senha,
            adm=comando.adm,
            ativo=comando.ativo,
            permissoes=comando.permissoes,
            usuario=uow.usuario,
        )

        await repo_dominio.adicionar(
            usuario=usuario,
        )
        await uow.commit()

    return usuario.id


async def remover_usuario(
    comando: RemoverUsuario, unidade_de_trabalho: UnidadeDeTrabalho
) -> UUID:
    from contextos_de_negocio import Dominio, UsuarioRepoDominio

    async with unidade_de_trabalho(Dominio.usuario) as uow:
        repo_dominio: UsuarioRepoDominio = uow.domain_repo

        filtros = Filtros(
            {
                "id": comando.id,
                "email": comando.email,
            }
        )
        usuario = await repo_dominio.consultar_um_por_filtros(filtros=filtros)
        usuario.remover(usuario=uow.usuario)

        await repo_dominio.remover(
            usuario=usuario,
        )
        await uow.commit()

    return usuario.id


async def cadastrar_usuario_publico(
    evento: UsuarioCriado, unidade_de_trabalho: UnidadeDeTrabalho
) -> UUID:
    from contextos_de_negocio import Dominio, UsuarioRepoDominio

    async with unidade_de_trabalho(Dominio.usuario) as uow:
        repo_dominio: UsuarioRepoDominio = uow.domain_repo

        filtros = Filtros(
            {
                "id": evento.id,
            }
        )
        usuario = await repo_dominio.consultar_um_por_filtros(filtros=filtros)

        usuario_publico = UsuarioPublico.retornar_agregado_para_cadastro(usuario=usuario)
        usuario_publico.cadastrar(
            usuario=uow.usuario,
        )

        await repo_dominio.adicionar_usuario_publico(
            usuario=usuario_publico,
        )
        await uow.commit()

    return usuario_publico.id


async def atualizar_usuario_publico(
    evento: UsuarioAtualizado, unidade_de_trabalho: UnidadeDeTrabalho
) -> UUID:
    from contextos_de_negocio import Dominio, UsuarioRepoDominio, UsuarioRepoConsulta

    async with unidade_de_trabalho(Dominio.usuario) as uow:
        repo_dominio: UsuarioRepoDominio = uow.domain_repo
        repo_consulta: UsuarioRepoConsulta = uow.view_repo

        filtros = Filtros(
            {
                "id": evento.id,
            }
        )
        usuario_privado = await repo_consulta.consultar_um_por_filtros(filtros=filtros)

        usuario_publico = await repo_dominio.consultar_usuario_publico_por_id(
            id=evento.id
        )
        usuario_publico.atualizar(
            usuario_privado=usuario_privado,
            usuario=uow.usuario,
        )

        await repo_dominio.adicionar_usuario_publico(
            usuario=usuario_publico,
        )
        await uow.commit()

    return usuario_publico.id


async def remover_usuario_publico(
    evento: UsuarioRemovido, unidade_de_trabalho: UnidadeDeTrabalho
) -> UUID:
    from contextos_de_negocio import Dominio, UsuarioRepoDominio

    async with unidade_de_trabalho(Dominio.usuario) as uow:
        repo_dominio: UsuarioRepoDominio = uow.domain_repo

        usuario_publico = await repo_dominio.consultar_usuario_publico_por_id(
            id=evento.id
        )
        usuario_publico.remover(usuario=uow.usuario)

        await repo_dominio.remover_usuario_publico(
            usuario=usuario_publico,
        )
        await uow.commit()

    return usuario_publico.id

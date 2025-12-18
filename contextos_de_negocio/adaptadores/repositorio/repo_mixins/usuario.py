from abc import ABC

from sqlalchemy import insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from contextos_de_negocio.adaptadores.orm.declarativo.usuario import UsuarioPublicoDB
from contextos_de_negocio.dominio.agregados.usuario import UsuarioPublico
from libs.utils.tipos_basicos import TipoDeOperacao


class UsuarioPublicoMixin(ABC):
    session: AsyncSession

    async def adicionar_usuario_publico(
        self,
        usuario: UsuarioPublico,
    ) -> None:
        dados = {
            "id": usuario.id,
            "empresa_id": usuario.empresa,
            "ativo": usuario.ativo,
            "email_criptografado": usuario.email_criptografado,
            "email_hash": usuario.email_hash,
            "senha_hash": usuario.senha_hash,
            "criado_por": usuario.criado_por,
            "criado_em": usuario.criado_em,
            "modificado_por": usuario.modificado_por,
            "ultima_modificacao_em": usuario.ultima_modificacao_em,
            "deletado_por": usuario.deletado_por,
            "deletado_em": usuario.deletado_em,
        }

        match usuario._tipo_de_operacao:
            case TipoDeOperacao.INSERCAO:
                operacao = insert(UsuarioPublicoDB).values(dados)
            case TipoDeOperacao.ATUALIZACAO:
                operacao = (
                    update(UsuarioPublicoDB)
                    .where(UsuarioPublicoDB.id == usuario.id)
                    .values(dados)
                )
            case _:
                raise ValueError(
                    "Tipo de operação não suportado para o repositório de domínio."
                )

        await self.session.execute(operacao)

    async def remover_usuario_publico(self, usuario: UsuarioPublico) -> None:
        if usuario._usa_soft_delete:
            dados = {
                "modificado_por": usuario.modificado_por,
                "ultima_modificacao_em": usuario.ultima_modificacao_em,
                "deletado_por": usuario.deletado_por,
                "deletado_em": usuario.deletado_em,
            }

            operacao = (
                update(UsuarioPublicoDB)
                .where(UsuarioPublicoDB.id == usuario.id)
                .values(dados)
            )
        else:
            operacao = delete(UsuarioPublicoDB).where(UsuarioPublicoDB.id == usuario.id)

        await self.session.execute(operacao)

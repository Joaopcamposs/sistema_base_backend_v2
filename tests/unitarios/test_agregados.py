"""
Testes unitários para os agregados do domínio.
"""

from uuid import uuid4

import pytest

from contextos_de_negocio.dominio.agregados.usuario import Usuario, UsuarioPublico
from contextos_de_negocio.dominio.eventos.usuario import (
    UsuarioCriado,
    UsuarioAtualizado,
    UsuarioRemovido,
)
from libs.utils.tipos_basicos import Email, CPF, TipoDeOperacao


class TestAgregadoUsuario:
    """Testes para o agregado Usuario."""

    @pytest.fixture
    def usuario_data(self) -> dict:
        """Dados base para criação de usuário."""
        return {
            "empresa": uuid4(),
            "nome": "João Teste",
            "email": Email("joao@teste.com"),
            "cpf": CPF(CPF.gerar()),
            "senha": "senha123",
            "ativo": True,
            "adm": False,
            "permissoes": ["leitura"],
        }

    def test_retornar_agregado_para_cadastro(self, usuario_data: dict) -> None:
        """Testa criação de agregado para cadastro."""
        usuario = Usuario.retornar_agregado_para_cadastro(**usuario_data)

        assert usuario.nome == usuario_data["nome"]
        assert usuario.email == usuario_data["email"]
        assert usuario.empresa == usuario_data["empresa"]
        assert usuario.ativo == usuario_data["ativo"]
        assert usuario.adm == usuario_data["adm"]
        assert usuario.id is not None

    def test_retornar_agregado_criptografa_senha(self, usuario_data: dict) -> None:
        """Testa que a senha é criptografada na criação."""
        usuario = Usuario.retornar_agregado_para_cadastro(**usuario_data)

        assert usuario._senha != usuario_data["senha"]
        assert usuario._senha.startswith("$2b$")

    def test_cadastrar_define_tipo_operacao_insercao(self, usuario_data: dict) -> None:
        """Testa que cadastrar define tipo de operação como INSERCAO."""
        usuario = Usuario.retornar_agregado_para_cadastro(**usuario_data)
        id_usuario = uuid4()

        usuario.cadastrar(id_usuario=id_usuario)

        assert usuario._tipo_de_operacao == TipoDeOperacao.INSERCAO
        assert usuario.criado_por == id_usuario
        assert usuario.criado_em is not None

    def test_cadastrar_adiciona_evento_usuario_criado(self, usuario_data: dict) -> None:
        """Testa que cadastrar adiciona evento UsuarioCriado."""
        usuario = Usuario.retornar_agregado_para_cadastro(**usuario_data)

        usuario.cadastrar(id_usuario=uuid4())

        assert len(usuario.eventos) == 1
        assert isinstance(usuario.eventos[0], UsuarioCriado)
        assert usuario.eventos[0].id == usuario.id

    def test_atualizar_modifica_campos(self, usuario_data: dict) -> None:
        """Testa que atualizar modifica os campos do usuário."""
        usuario = Usuario.retornar_agregado_para_cadastro(**usuario_data)
        id_usuario = uuid4()

        novo_nome = "João Atualizado"
        novo_email = Email("joao.novo@teste.com")
        novo_cpf = CPF(CPF.gerar())

        usuario.atualizar(
            nome=novo_nome,
            email=novo_email,
            cpf=novo_cpf,
            senha="nova_senha",
            adm=True,
            ativo=False,
            permissoes=["admin"],
            id_usuario=id_usuario,
        )

        assert usuario.nome == novo_nome
        assert usuario.email == novo_email
        assert usuario.adm is True
        assert usuario.ativo is False
        assert usuario._tipo_de_operacao == TipoDeOperacao.ATUALIZACAO

    def test_atualizar_adiciona_evento_usuario_atualizado(
        self, usuario_data: dict
    ) -> None:
        """Testa que atualizar adiciona evento UsuarioAtualizado."""
        usuario = Usuario.retornar_agregado_para_cadastro(**usuario_data)

        usuario.atualizar(
            nome="Novo Nome",
            email=Email("novo@teste.com"),
            cpf=CPF(CPF.gerar()),
            senha="nova_senha",
            adm=False,
            ativo=True,
            permissoes=[],
            id_usuario=uuid4(),
        )

        assert len(usuario.eventos) == 1
        assert isinstance(usuario.eventos[0], UsuarioAtualizado)

    def test_remover_define_campos_deletado(self, usuario_data: dict) -> None:
        """Testa que remover define campos de deleção."""
        usuario = Usuario.retornar_agregado_para_cadastro(**usuario_data)
        id_usuario = uuid4()

        usuario.remover(id_usuario=id_usuario)

        assert usuario._tipo_de_operacao == TipoDeOperacao.REMOCAO
        assert usuario.deletado_por == id_usuario
        assert usuario.deletado_em is not None

    def test_remover_adiciona_evento_usuario_removido(self, usuario_data: dict) -> None:
        """Testa que remover adiciona evento UsuarioRemovido."""
        usuario = Usuario.retornar_agregado_para_cadastro(**usuario_data)

        usuario.remover(id_usuario=uuid4())

        assert len(usuario.eventos) == 1
        assert isinstance(usuario.eventos[0], UsuarioRemovido)

    def test_usuario_hashable(self, usuario_data: dict) -> None:
        """Testa que usuário é hashable (pode ser adicionado a set)."""
        usuario = Usuario.retornar_agregado_para_cadastro(**usuario_data)

        usuarios = {usuario}
        assert usuario in usuarios


class TestAgregadoUsuarioPublico:
    """Testes para o agregado UsuarioPublico."""

    @pytest.fixture
    def usuario_privado(self) -> Usuario:
        """Cria um usuário privado para teste."""
        usuario = Usuario.retornar_agregado_para_cadastro(
            empresa=uuid4(),
            nome="João",
            email=Email("joao@teste.com"),
            cpf=CPF(CPF.gerar()),
            senha="senha123",
            ativo=True,
            adm=False,
            permissoes=[],
        )
        usuario.cadastrar(id_usuario=uuid4())
        return usuario

    def test_retornar_agregado_para_cadastro_publico(
        self, usuario_privado: Usuario
    ) -> None:
        """Testa criação de agregado público a partir do privado."""
        usuario_publico = UsuarioPublico.retornar_agregado_para_cadastro(
            usuario=usuario_privado
        )

        assert usuario_publico.id == usuario_privado.id
        assert usuario_publico.empresa == usuario_privado.empresa
        assert usuario_publico.ativo == usuario_privado.ativo
        assert usuario_publico.email_criptografado is not None
        assert usuario_publico.email_hash is not None

    def test_email_hash_e_consistente(self, usuario_privado: Usuario) -> None:
        """Testa que o hash do email é consistente."""
        usuario_publico = UsuarioPublico.retornar_agregado_para_cadastro(
            usuario=usuario_privado
        )

        expected_hash = UsuarioPublico.hash_email(usuario_privado.email)
        assert usuario_publico.email_hash == expected_hash

    def test_cadastrar_publico(self, usuario_privado: Usuario) -> None:
        """Testa cadastro de usuário público."""
        usuario_publico = UsuarioPublico.retornar_agregado_para_cadastro(
            usuario=usuario_privado
        )
        id_usuario = uuid4()

        usuario_publico.cadastrar(id_usuario=id_usuario)

        assert usuario_publico._tipo_de_operacao == TipoDeOperacao.INSERCAO
        assert usuario_publico.criado_por == id_usuario

    def test_atualizar_publico(self, usuario_privado: Usuario) -> None:
        """Testa atualização de usuário público."""
        usuario_publico = UsuarioPublico.retornar_agregado_para_cadastro(
            usuario=usuario_privado
        )
        id_usuario = uuid4()
        novo_email = Email("novo@teste.com")

        usuario_publico.atualizar(
            email=novo_email,
            senha="nova_senha_hash",
            ativo=False,
            id_usuario=id_usuario,
        )

        assert usuario_publico._tipo_de_operacao == TipoDeOperacao.ATUALIZACAO
        assert usuario_publico.ativo is False
        assert usuario_publico.email_hash == UsuarioPublico.hash_email(novo_email)

    def test_remover_publico(self, usuario_privado: Usuario) -> None:
        """Testa remoção de usuário público."""
        usuario_publico = UsuarioPublico.retornar_agregado_para_cadastro(
            usuario=usuario_privado
        )
        id_usuario = uuid4()

        usuario_publico.remover(id_usuario=id_usuario)

        assert usuario_publico._tipo_de_operacao == TipoDeOperacao.REMOCAO
        assert usuario_publico.deletado_por == id_usuario
        assert usuario_publico.deletado_em is not None

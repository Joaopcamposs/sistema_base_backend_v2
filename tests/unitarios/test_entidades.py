"""
Testes unitários para as entidades do domínio.
"""

from datetime import datetime
from uuid import uuid4


from libs.ddd.dominio.entidades import CamposBase, SegurancaDoUsuario
from libs.utils.tipos_basicos import Email, CPF


class TestCamposBase:
    """Testes para a classe CamposBase."""

    def test_campos_base_valores_default(self) -> None:
        """Testa que os campos base têm valores padrão None."""
        from dataclasses import dataclass

        @dataclass(kw_only=True)
        class EntidadeTeste(CamposBase):
            nome: str

        entidade = EntidadeTeste(nome="teste")

        assert entidade.criado_por is None
        assert entidade.criado_em is None
        assert entidade.modificado_por is None
        assert entidade.ultima_modificacao_em is None
        assert entidade.deletado_por is None
        assert entidade.deletado_em is None

    def test_campos_base_com_valores(self) -> None:
        """Testa CamposBase com valores definidos."""
        from dataclasses import dataclass

        @dataclass(kw_only=True)
        class EntidadeTeste(CamposBase):
            nome: str

        user_id = uuid4()
        now = datetime.now()

        entidade = EntidadeTeste(
            nome="teste",
            criado_por=user_id,
            criado_em=now,
        )

        assert entidade.criado_por == user_id
        assert entidade.criado_em == now


class TestSegurancaDoUsuario:
    """Testes para a classe SegurancaDoUsuario."""

    def test_criptografar_senha(self) -> None:
        """Testa criptografia de senha."""
        senha = "minha_senha_123"
        senha_hash = SegurancaDoUsuario.criptografar_senha(senha)

        assert senha_hash != senha
        assert senha_hash.startswith("$2b$")

    def test_verificar_senha_correta(self) -> None:
        """Testa verificação de senha correta."""
        from dataclasses import dataclass

        @dataclass
        class UsuarioTeste(SegurancaDoUsuario):
            _senha: str

        senha = "minha_senha_123"
        senha_hash = SegurancaDoUsuario.criptografar_senha(senha)

        usuario = UsuarioTeste(_senha=senha_hash)
        assert usuario.verificar_senha(senha) is True

    def test_verificar_senha_incorreta(self) -> None:
        """Testa verificação de senha incorreta."""
        from dataclasses import dataclass

        @dataclass
        class UsuarioTeste(SegurancaDoUsuario):
            _senha: str

        senha = "minha_senha_123"
        senha_hash = SegurancaDoUsuario.criptografar_senha(senha)

        usuario = UsuarioTeste(_senha=senha_hash)
        assert usuario.verificar_senha("senha_errada") is False

    def test_hash_email(self) -> None:
        """Testa hash de email."""
        email = "teste@teste.com"
        email_hash = SegurancaDoUsuario.hash_email(email)

        assert len(email_hash) == 64
        assert email_hash == SegurancaDoUsuario.hash_email(email)

    def test_hash_email_case_insensitive(self) -> None:
        """Testa que hash de email é case insensitive."""
        hash1 = SegurancaDoUsuario.hash_email("TESTE@TESTE.COM")
        hash2 = SegurancaDoUsuario.hash_email("teste@teste.com")

        assert hash1 == hash2

    def test_criptografar_descriptografar_email(self) -> None:
        """Testa criptografia e descriptografia de email."""
        email = "teste@teste.com"

        email_cripto = SegurancaDoUsuario.criptografar_email(email)
        email_decripto = SegurancaDoUsuario.descriptografar_email(email_cripto)

        assert email_cripto != email.encode()
        assert email_decripto == email


class TestUsuarioEntidade:
    """Testes para a entidade Usuario."""

    def test_criar_usuario(self) -> None:
        """Testa criação de entidade Usuario."""
        from contextos_de_negocio.dominio.entidades.usuario import Usuario

        empresa_id = uuid4()
        usuario = Usuario(
            id=uuid4(),
            empresa=empresa_id,
            nome="Teste",
            email=Email("teste@teste.com"),
            cpf=CPF(CPF.gerar()),
            ativo=True,
            adm=False,
            _senha="hash",
            permissoes=[],
        )

        assert usuario.nome == "Teste"
        assert usuario.email == "teste@teste.com"
        assert usuario.ativo is True
        assert usuario.adm is False

    def test_usuario_com_permissoes(self) -> None:
        """Testa Usuario com lista de permissões."""
        from contextos_de_negocio.dominio.entidades.usuario import Usuario

        permissoes = ["criar_usuario", "deletar_usuario"]
        usuario = Usuario(
            id=uuid4(),
            empresa=uuid4(),
            nome="Admin",
            email=Email("admin@teste.com"),
            cpf=CPF(CPF.gerar()),
            ativo=True,
            adm=True,
            _senha="hash",
            permissoes=permissoes,
        )

        assert usuario.permissoes == permissoes
        assert len(usuario.permissoes) == 2


class TestEmpresaEntidade:
    """Testes para a entidade Empresa."""

    def test_criar_empresa(self) -> None:
        """Testa criação de entidade Empresa."""
        from contextos_de_negocio.dominio.entidades.empresa import Empresa

        empresa = Empresa(
            id=uuid4(),
            razao_social="Empresa Teste LTDA",
            nome_fantasia="Empresa Teste",
            nome_responsavel="João",
            email=Email("empresa@teste.com"),
            cpf=CPF(CPF.gerar()),
            cnpj="12345678000190",
            ativo=True,
        )

        assert empresa.razao_social == "Empresa Teste LTDA"
        assert empresa.nome_fantasia == "Empresa Teste"
        assert empresa.ativo is True

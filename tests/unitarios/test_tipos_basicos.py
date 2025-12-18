"""
Testes unitários para os tipos básicos do sistema.
"""

import pytest

from libs.utils.tipos_basicos import CPF, CNPJ, Email, TipoDeOperacao


class TestCPF:
    """Testes para a classe CPF."""

    def test_cpf_valido_com_digitos(self) -> None:
        """Testa CPF válido apenas com dígitos."""
        cpf_valido = CPF.gerar()
        cpf = CPF(cpf_valido)
        assert str(cpf) == cpf_valido

    def test_cpf_valido_com_formatacao(self) -> None:
        """Testa CPF válido com formatação (pontos e traços)."""
        cpf_formatado = "468.659.548-74"
        cpf = CPF(cpf_formatado)
        assert str(cpf) == "46865954874"

    def test_cpf_invalido_levanta_excecao(self) -> None:
        """Testa que CPF inválido levanta ValueError."""
        with pytest.raises(ValueError, match="CPF inválido"):
            CPF("11111111111")

    def test_cpf_vazio_levanta_excecao(self) -> None:
        """Testa que CPF vazio levanta ValueError."""
        with pytest.raises(ValueError):
            CPF("")

    def test_cpf_gerar_retorna_cpf_valido(self) -> None:
        """Testa que  gerar() retorna um CPF válido."""
        cpf_gerado = CPF.gerar()
        cpf = CPF(cpf_gerado)
        assert len(str(cpf)) == 11

    def test_cpf_somente_digitos(self) -> None:
        """Testa  somente_digitos."""
        resultado = CPF.somente_digitos("123.456.789-00")
        assert resultado == "12345678900"


class TestCNPJ:
    """Testes para a classe CNPJ."""

    def test_cnpj_com_formatacao(self) -> None:
        """Testa CNPJ com formatação."""
        cnpj = CNPJ("12.345.678/0001-90")
        assert cnpj == "12345678000190"

    def test_cnpj_apenas_digitos(self) -> None:
        """Testa CNPJ apenas com dígitos."""
        cnpj = CNPJ("12345678000190")
        assert cnpj == "12345678000190"

    def test_cnpj_none_retorna_string_vazia(self) -> None:
        """Testa que CNPJ None retorna string vazia."""
        cnpj = CNPJ(None)
        assert cnpj == ""

    def test_cnpj_vazio_retorna_string_vazia(self) -> None:
        """Testa que CNPJ vazio retorna string vazia."""
        cnpj = CNPJ("")
        assert cnpj == ""


class TestEmail:
    """Testes para a classe Email."""

    def test_email_lowercase(self) -> None:
        """Testa que email é convertido para lowercase."""
        email = Email("TESTE@TESTE.COM")
        assert email == "teste@teste.com"

    def test_email_mixed_case(self) -> None:
        """Testa email com letras mistas."""
        email = Email("Teste@Teste.Com")
        assert email == "teste@teste.com"

    def test_email_ja_lowercase(self) -> None:
        """Testa email já em lowercase."""
        email = Email("teste@teste.com")
        assert email == "teste@teste.com"


class TestTipoDeOperacao:
    """Testes para o enum TipoDeOperacao."""

    def test_tipo_insercao(self) -> None:
        """Testa valor do tipo INSERCAO."""
        assert TipoDeOperacao.INSERCAO.value == "insercao"

    def test_tipo_atualizacao(self) -> None:
        """Testa valor do tipo ATUALIZACAO."""
        assert TipoDeOperacao.ATUALIZACAO.value == "atualizacao"

    def test_tipo_remocao(self) -> None:
        """Testa valor do tipo REMOCAO."""
        assert TipoDeOperacao.REMOCAO.value == "remocao"

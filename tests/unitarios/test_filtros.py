"""
Testes unitários para a classe Filtros.
"""

from libs.ddd.visualizadores.filtro import Filtros


class TestFiltros:
    """Testes para a classe Filtros."""

    def test_filtros_remove_valores_none(self) -> None:
        """Testa que valores None são removidos."""
        filtros = Filtros({"nome": "João", "email": None, "ativo": True})

        assert "nome" in filtros
        assert "ativo" in filtros
        assert "email" not in filtros

    def test_filtros_mantem_valores_validos(self) -> None:
        """Testa que valores válidos são mantidos."""
        filtros = Filtros({"nome": "João", "idade": 30, "ativo": False})

        assert filtros["nome"] == "João"
        assert filtros["idade"] == 30
        assert filtros["ativo"] is False

    def test_filtros_vazio(self) -> None:
        """Testa filtros com dicionário vazio."""
        filtros = Filtros({})

        assert len(filtros) == 0

    def test_filtros_todos_none(self) -> None:
        """Testa filtros onde todos os valores são None."""
        filtros = Filtros({"a": None, "b": None, "c": None})

        assert len(filtros) == 0

    def test_filtros_str(self) -> None:
        """Testa representação string dos filtros."""
        filtros = Filtros({"nome": "João"})

        assert str(filtros) == "{'nome': 'João'}"

    def test_filtros_mantem_zero(self) -> None:
        """Testa que valor zero é mantido (não confundido com None)."""
        filtros = Filtros({"quantidade": 0, "nome": None})

        assert "quantidade" in filtros
        assert filtros["quantidade"] == 0

    def test_filtros_mantem_string_vazia(self) -> None:
        """Testa que string vazia é mantida."""
        filtros = Filtros({"nome": "", "email": None})

        assert "nome" in filtros
        assert filtros["nome"] == ""

    def test_filtros_mantem_lista_vazia(self) -> None:
        """Testa que lista vazia é mantida."""
        filtros = Filtros({"itens": [], "valor": None})

        assert "itens" in filtros
        assert filtros["itens"] == []

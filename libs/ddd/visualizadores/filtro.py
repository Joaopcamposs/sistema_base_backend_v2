from typing import Any


class Filtros(dict):
    """
    Classe base para filtros genéricos.
    Converte automaticamente os campos não nulos em um dicionário utilizável para consultas.
    """

    def __init__(self, filtros: dict):
        super().__init__()
        self.update(self.to_query(filtros))

    def __new__(cls, *args: dict[str, Any], **kwargs: dict[str, Any]) -> "Filtros":
        return super().__new__(cls)

    @staticmethod
    def to_query(filtros: dict[str, Any]) -> dict[str, Any]:
        """
        Retorna um dicionário contendo somente os campos não nulos.
        """
        return {key: value for key, value in filtros.items() if value is not None}

    def __str__(self) -> str:
        return str(dict(self))

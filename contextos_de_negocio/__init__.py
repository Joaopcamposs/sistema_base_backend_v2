from enum import Enum

from contextos_de_negocio.adaptadores.repositorio.repo_consulta.empresa import (
    EmpresaRepoConsulta,
)
from contextos_de_negocio.adaptadores.repositorio.repo_consulta.usuario import (
    UsuarioRepoConsulta,
)
from contextos_de_negocio.adaptadores.repositorio.repo_dominio.empresa import (
    EmpresaRepoDominio,
)
from contextos_de_negocio.adaptadores.repositorio.repo_dominio.usuario import (
    UsuarioRepoDominio,
)


class Dominio(Enum):
    usuario = (UsuarioRepoDominio, UsuarioRepoConsulta)
    empresa = (EmpresaRepoDominio, EmpresaRepoConsulta)

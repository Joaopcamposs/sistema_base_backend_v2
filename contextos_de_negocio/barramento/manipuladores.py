from contextos_de_negocio.dominio.comandos.empresa import (
    CadastrarEmpresa,
    AtualizarEmpresa,
    RemoverEmpresa,
)
from contextos_de_negocio.dominio.comandos.teste import ComandoTeste
from contextos_de_negocio.dominio.comandos.usuario import (
    CadastrarUsuario,
    AtualizarUsuario,
    RemoverUsuario,
)

from contextos_de_negocio.dominio.eventos.empresa import (
    EmpresaCriada,
    EmpresaAtualizada,
    EmpresaRemovida,
)
from contextos_de_negocio.dominio.eventos.teste import EventoTeste, EventoTesteAssincrono
from contextos_de_negocio.dominio.eventos.usuario import (
    UsuarioCriado,
    UsuarioAtualizado,
    UsuarioRemovido,
    ChegouAHoraDeCriarUsuarioInicialDaEmpresa,
    ChegouAHoraDeCriarUsuarioADMDaEmpresa,
)
from contextos_de_negocio.servicos.executores.empresa import (
    cadastrar_empresa,
    atualizar_empresa,
    remover_empresa,
)
from contextos_de_negocio.servicos.executores.teste import (
    evento_teste,
    evento_teste_assincrono,
    comando_teste,
)
from contextos_de_negocio.servicos.executores.usuario import (
    remover_usuario,
    atualizar_usuario,
    cadastrar_usuario,
    cadastrar_usuario_publico,
    atualizar_usuario_publico,
    remover_usuario_publico,
)
from libs.ddd.barramento import ManipuladoresDeEventos, ManipuladoresDeComandos

EVENT_HANDLERS: ManipuladoresDeEventos = ManipuladoresDeEventos(
    {
        EventoTeste: [evento_teste],
        EventoTesteAssincrono: [evento_teste_assincrono],
        # usuario
        UsuarioCriado: [cadastrar_usuario_publico],
        UsuarioAtualizado: [atualizar_usuario_publico],
        UsuarioRemovido: [remover_usuario_publico],
        # empresa
        EmpresaCriada: [],
        EmpresaAtualizada: [],
        EmpresaRemovida: [],
        ChegouAHoraDeCriarUsuarioInicialDaEmpresa: [cadastrar_usuario],
        ChegouAHoraDeCriarUsuarioADMDaEmpresa: [cadastrar_usuario],
    }
)

COMMAND_HANDLERS: ManipuladoresDeComandos = ManipuladoresDeComandos(
    {
        ComandoTeste: comando_teste,
        # usuario
        CadastrarUsuario: cadastrar_usuario,
        AtualizarUsuario: atualizar_usuario,
        RemoverUsuario: remover_usuario,
        # empresa
        CadastrarEmpresa: cadastrar_empresa,
        AtualizarEmpresa: atualizar_empresa,
        RemoverEmpresa: remover_empresa,
    }
)

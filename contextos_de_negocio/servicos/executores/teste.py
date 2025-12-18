from contextos_de_negocio.dominio.comandos.teste import ComandoTeste
from contextos_de_negocio.dominio.eventos.teste import EventoTeste, EventoTesteAssincrono
from contextos_de_negocio.barramento.unidade_de_trabalho import UnidadeDeTrabalho


async def comando_teste(comando: ComandoTeste, uow: UnidadeDeTrabalho) -> str:
    """
    Comando de teste.

    :return: None
    """
    print(comando.mensagem)
    uow.adicionar_evento_fora_de_agregado(EventoTeste(mensagem="evento printado"))
    uow.adicionar_evento_fora_de_agregado(
        EventoTesteAssincrono(mensagem="evento printado assincrono")
    )
    return "comando printado com sucesso!"


async def evento_teste(evento: EventoTeste, uow: UnidadeDeTrabalho) -> None:
    """
    Comando de teste.

    :return: None
    """
    print(evento.mensagem)


async def evento_teste_assincrono(
    evento: EventoTesteAssincrono, uow: UnidadeDeTrabalho
) -> None:
    """
    Comando de teste.

    :return: None
    """
    print(evento.mensagem)

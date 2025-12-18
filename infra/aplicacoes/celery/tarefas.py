from typing import Any

from contextos_de_negocio.dominio.entidades.usuario import Usuario
from celery.local import PromiseProxy

from infra.aplicacoes.celery import celery_app
from libs.ddd.barramento import Evento, BarramentoDeMensagens


def tarefa_celery(*args: dict[str, Any], **kwargs: dict[str, Any]) -> PromiseProxy:
    max_retries = kwargs.pop("max_retries", 1)
    kwargs["bind"] = True
    kwargs["trail"] = True
    retry_backoff = kwargs.pop("retry_backoff", 5)
    retry_backoff_max = kwargs.pop("retry_backoff_max", 700)
    retry_jitter = kwargs.pop("retry_jitter", False)
    return celery_app.task(
        *args,
        autoretry_for=(Exception,),
        retry_kwargs={"max_retries": max_retries},
        max_retries=max_retries,
        retry_backoff=retry_backoff,
        retry_backoff_max=retry_backoff_max,
        retry_jitter=retry_jitter,
        **kwargs,
    )


def tratar_evento_asyncrono(  # type: ignore[no-untyped-def]
    self,
    evento: Evento,
    usuario: Usuario | None = None,
) -> None:
    from contextos_de_negocio.barramento.bootstrap import bootstrap
    import sentry_sdk
    import asyncio

    async def executar(barramento: BarramentoDeMensagens, evento: Evento) -> None:
        await barramento.handle(evento)

    nome = f"Tratando evento asyncrono [{evento.__class__.__name__}]"

    contexto = sentry_sdk.start_transaction(
        name="Tratando evento asyncrono",
        op="task",
        description=nome,
        sampled=True,
    )
    with contexto as span:
        span.set_tag("name", nome)
        try:
            # A execução assíncrona começou, super importante alterar a flag do evento
            # para não ser executado de forma assíncrona novamente,
            # caso contrário o celery entrará num loop infinito de tasks
            evento.executar_de_forma_assincrona = False

            bus = bootstrap(usuario=usuario, subir_erros_de_eventos=True)

            # isso deve rodar dentro do asyncio.run devido a estrutura de funcoes async
            asyncio.run(executar(bus, evento))

        except Exception as erro:
            span.set_tag("houve_erro", True)
            span.set_tag("error", str(erro))
            raise erro


task_tratar_evento_asyncrono = tarefa_celery()(tratar_evento_asyncrono)

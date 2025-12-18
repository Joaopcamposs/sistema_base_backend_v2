# Sistema Base Backend V2

Sistema base para criar repositórios de sistemas de gerenciamento para diferentes negócios: dentistas, advogados, médicos, etc.

## Tecnologias

- **Python 3.11+**
- **FastAPI** - Framework web
- **SQLAlchemy** - ORM assíncrono
- **Celery** - Processamento assíncrono
- **PostgreSQL** - Banco de dados
- **Redis** - Message broker

## Arquitetura

- **DDD (Domain-Driven Design)** - Entidades, Agregados, Comandos, Eventos
- **Event-Driven** - Barramento de mensagens desacoplado
- **Repository Pattern** - Separação de escrita/leitura
- **Unit of Work** - Gerenciamento de transações

Veja [docs/ARQUITETURA.md](docs/ARQUITETURA.md) para detalhes.

## Setup

```bash
# Instalar dependências
uv sync

# Subir ambiente de desenvolvimento
make compose

# Rodar aplicação local
uvicorn contextos_de_negocio.main:app --reload
```

## Testes

```bash
# Testes unitários (sem banco)
make test-unit

# Testes de integração (com Docker)
make test-compose

# Todos os testes locais
make test-local
```

## Estrutura

```
├── contextos_de_negocio/   # Bounded Contexts
├── infra/                  # Infraestrutura (Celery, DB)
├── libs/ddd/               # Core DDD (preparado para lib externa)
└── tests/                  # Testes unitários e integração
```

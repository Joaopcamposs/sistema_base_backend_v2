# Arquitetura do Sistema Base Backend V2

Este documento descreve a arquitetura do projeto e as melhorias implementadas para torná-lo um sistema base desacoplado e testável.

## Estrutura do Projeto

```
sistema_base_backend_v2/
├── contextos_de_negocio/       # Bounded Contexts do DDD
│   ├── adaptadores/            # Repositórios e ORM
│   ├── barramento/             # Bootstrap e handlers específicos
│   ├── dominio/                # Entidades, Agregados, Comandos, Eventos
│   ├── pontos_de_entrada/      # APIs (FastAPI)
│   └── servicos/               # Executores de comandos/eventos
├── infra/                      # Infraestrutura
│   ├── aplicacoes/celery/      # Configuração Celery
│   └── banco_de_dados/         # Configuração SQLAlchemy
├── libs/                       # Bibliotecas reutilizáveis (preparadas para lib externa)
│   ├── ddd/                    # Core DDD desacoplado
│   │   ├── adaptadores/        # Implementações concretas (Celery, Sentry)
│   │   ├── dominio/            # Entidades e Agregados base
│   │   ├── visualizadores/     # Filtros e helpers
│   │   ├── barramento.py       # Message Bus com protocolos abstratos
│   │   ├── bootstrap.py        # Configuração do barramento
│   │   └── unidade_de_trabalho.py  # Unit of Work
│   └── utils/                  # Utilitários (tipos, constantes)
└── tests/                      # Testes
    ├── unitarios/              # Testes unitários (sem I/O)
    └── integracao/             # Testes de integração
```

## Padrões Arquiteturais

### DDD (Domain-Driven Design)
- **Entidades**: Classes de dados com identidade (`@/libs/ddd/dominio/entidades.py`)
- **Agregados**: Entidades raiz com eventos de domínio (`@/libs/ddd/dominio/agregado.py`)
- **Comandos**: Intenções de mudança no sistema
- **Eventos**: Fatos que aconteceram no sistema

### Event-Driven Architecture
- **Barramento de Mensagens**: Processa comandos e eventos de forma desacoplada
- **Eventos Assíncronos**: Suporte a processamento via Celery

### Repository Pattern
- **RepositorioDominio**: Escrita e leitura de agregados
- **RepositorioConsulta**: Somente leitura para queries

### Unit of Work
- Gerencia transações e coleta de eventos dos agregados

## Desacoplamento do Barramento

O barramento foi refatorado para ser **completamente desacoplado** de implementações específicas:

### Protocolos Abstratos

```python
# libs/ddd/barramento.py

@runtime_checkable
class DespachadorAssincrono(Protocol):
    """Protocolo para despachadores de eventos assíncronos."""
    def despachar(self, evento: Evento, usuario: Any) -> None: ...

@runtime_checkable
class ReportadorDeErros(Protocol):
    """Protocolo para reportadores de erros."""
    def capturar_excecao(self, erro: Exception) -> None: ...
```

### Implementações Concretas

```python
# libs/ddd/adaptadores/despachadores.py

class DespachadorCelery:
    """Usa Celery para processar eventos assíncronos."""

class ReportadorSentry:
    """Usa Sentry para reportar erros."""

class DespachadorNulo:
    """Para testes - não faz nada."""

class ReportadorNulo:
    """Para testes - apenas loga."""
```

### Injeção de Dependências

O bootstrap configura automaticamente os adaptadores baseado no ambiente:

```python
# Em ambiente de teste (TEST_ENV=true)
despachador = DespachadorNulo()
reportador = ReportadorNulo()

# Em produção
despachador = DespachadorCelery()
reportador = ReportadorSentry()
```

## Executando Testes

### Testes Unitários (sem banco de dados)

```bash
make test-unit
# ou
TEST_ENV=true pytest tests/unitarios/ -v
```

### Testes de Integração (com banco de dados via Docker)

```bash
make test-compose
```

### Todos os Testes Locais

```bash
make test-local
```

## Docker Compose

### Desenvolvimento
```bash
make compose
```

### Testes
```bash
make test-compose
```

## Preparação para Lib Externa

O módulo `libs/ddd/` foi projetado para ser extraído como biblioteca externa:

1. **Sem dependências de contexto**: Não importa de `contextos_de_negocio/`
2. **Protocolos abstratos**: Permite injeção de implementações
3. **Bootstrap configurável**: Aceita adaptadores customizados

Para extrair como lib:
1. Copie `libs/ddd/` para novo repositório
2. Remova imports de `contextos_de_negocio.dominio.entidades.usuario`
3. Use tipo genérico para `Usuario` no bootstrap

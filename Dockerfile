FROM python:3.11.9-slim

# Cria diretório da app
WORKDIR /sistema_base_backend_v2

# Instalações básicas
RUN apt-get update && apt-get install -y curl build-essential

# Copia a aplicação
COPY . .

# Instala dependências
RUN pip install --upgrade pip
RUN pip install uv
RUN uv sync && uv venv

# Adiciona o .venv/bin ao PATH do container
ENV PATH="/sistema_base_backend_v2/.venv/bin:$PATH"
ENV PYTHONPATH=/sistema_base_backend_v2

# Comando padrão
CMD ["uvicorn", "contextos_de_negocio.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "uvicorn_logging.json"]

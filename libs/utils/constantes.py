import base64
import json
import os
from pathlib import Path
from typing import Final
from dotenv import load_dotenv

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


load_dotenv()


def get_config_value(key: str, default=None):
    """
    Retorna o valor da variável de configuração buscando na seguinte ordem:
    1. Variáveis de ambiente (.env ou docker env)
    2. Arquivo secrets.json
    3. Valor default (caso informado)
    """
    return os.getenv(key.upper()) or config.get(key.lower()) or default


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
with open(BASE_DIR / "secrets.json") as f:
    config = json.load(f)

DB_HOST = get_config_value("DB_HOST", "localhost")
DB_PASSWORD = get_config_value("DB_PASSWORD", "password")
DB_USER = get_config_value("DB_USER", "postgres")
DB_NAME = get_config_value("DB_NAME", "postgres")

PREFIXO_USUARIO_ADM = get_config_value("PREFIXO_USUARIO_ADM")
EMAIL_PRIMEIRO_USUARIO = get_config_value("EMAIL_PRIMEIRO_USUARIO")
SENHA_PRIMEIRO_USUARIO = get_config_value("SENHA_PRIMEIRO_USUARIO")
CPF_PRIMEIRO_USUARIO = get_config_value("CPF_PRIMEIRO_USUARIO")
AES_KEY = base64.b64decode(get_config_value("AES_KEY", "").encode())
CHAVE_SECRETA = get_config_value("CHAVE_SECRETA")

SECRET_KEY = get_config_value("SECRET_KEY", "")
ALGORITHM = get_config_value("ALGORITHM", "")
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_config_value("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

NAO_DELETADO: Final[dict] = {"deletado_em": None}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/token",
)

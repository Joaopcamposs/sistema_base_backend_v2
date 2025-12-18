import hashlib
import os
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from libs.utils.constantes import pwd_context, AES_KEY


@dataclass(kw_only=True)
class CamposBase(ABC):
    criado_por: UUID | None = None
    criado_em: datetime | None = None
    modificado_por: UUID | None = None
    ultima_modificacao_em: datetime | None = None
    deletado_por: UUID | None = None
    deletado_em: datetime | None = None


@dataclass
class SegurancaDoUsuario:
    _senha: str

    def verificar_senha(self, senha: str) -> bool:
        senhas_conferem = pwd_context.verify(secret=senha, hash=self._senha)
        return senhas_conferem

    @staticmethod
    def criptografar_senha(senha: str) -> str:
        senha_criptografada = pwd_context.hash(secret=senha)
        return senha_criptografada

    @staticmethod
    def hash_email(email: str) -> str:
        return hashlib.sha256(email.strip().lower().encode()).hexdigest()

    @staticmethod
    def criptografar_email(email: str) -> bytes:
        aesgcm = AESGCM(AES_KEY)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, email.encode(), None)
        return nonce + ct

    @staticmethod
    def descriptografar_email(email: bytes) -> str:
        aesgcm = AESGCM(AES_KEY)
        nonce, ct = email[:12], email[12:]
        return aesgcm.decrypt(nonce, ct, None).decode()

import pandas as pd
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, List
import logging
import uuid
from api.models import TokenData

# Reutiliza o logger definido em main.py
logger = logging.getLogger("api_logger")

# Configuração de autenticação JWT
SECRET_KEY = "minha-senha"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# Lista em memória para armazenar tokens revogados
revoked_tokens = set()

# Usuários fictícios para autenticação
try:
    fake_users_db = {"admin": {"username": "admin", "password": "admin123"}}
    logger.info("Usuários fictícios inicializados com sucesso")
except Exception as e:
    logger.error(f"Erro ao inicializar fake_users_db: {str(e)}", exc_info=True)
    raise

# Variável global para armazenar o DataFrame
books_df = None


def load_books_data() -> pd.DataFrame:
    """
    Carrega os dados do CSV e retorna o DataFrame.
    Método chamado na inicialização da aplicação e também ao finalizar o scrape.
    """
    global books_df
    try:
        books_df = pd.read_csv(
            "data/books.csv",
            dtype={"id": int, "title": str, "href": str, "price": float, "rating": int, "availability": str, "category": str, "image_url": str},
        )
        logger.info("Dados do CSV carregados com sucesso")
    except Exception as e:
        logger.error(f"Erro ao carregar books.csv: {str(e)}", exc_info=True)
        books_df = pd.DataFrame()
    return books_df


# Carrega o CSV na inicialização da aplicação
books_df = load_books_data()


def get_books_data() -> pd.DataFrame:
    """
    Retorna o DataFrame com os dados dos livros.
    """
    if books_df is None or books_df.empty:
        logger.warning("DataFrame de livros está vazio ou não carregado")
        return load_books_data()
    return books_df


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Valida o token JWT e retorna os dados do usuário.
    Verifica se o token está revogado.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        jti: str = payload.get("jti")
        if username is None or jti is None:
            logger.error("Token JWT sem 'sub' ou 'jti'")
            raise credentials_exception
        if jti in revoked_tokens:
            logger.error(f"Token revogado usado: jti={jti}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revogado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(username=username, jti=jti)
    except JWTError as e:
        logger.error(f"Erro ao decodificar token JWT: {str(e)}")
        raise credentials_exception

    user = fake_users_db.get(token_data.username)
    if user is None:
        logger.error(f"Usuário {token_data.username} não encontrado")
        raise credentials_exception
    logger.info(f"Usuário {token_data.username} autenticado com sucesso")
    return user


def create_access_token(data: dict) -> str:
    """
    Cria um token JWT com expiração e identificador único (jti).
    """
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        jti = str(uuid.uuid4())  # Gera um identificador único para o token
        to_encode.update({"exp": expire, "jti": jti})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Token JWT criado com sucesso: jti={jti}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Erro ao criar token JWT: {str(e)}", exc_info=True)
        raise


def verify_password(plain_password: str, stored_password: str) -> bool:
    """
    Verifica se a senha fornecida corresponde à senha armazenada.
    """
    try:
        result = plain_password == stored_password
        logger.info(f"Verificação de senha: {'sucesso' if result else 'falha'}")
        return result
    except Exception as e:
        logger.error(f"Erro ao verificar senha: {str(e)}", exc_info=True)
        return False


def revoke_token(jti: str):
    """
    Adiciona um token à lista de tokens revogados.
    """
    try:
        revoked_tokens.add(jti)
        logger.info(f"Token revogado: jti={jti}")
    except Exception as e:
        logger.error(f"Erro ao revogar token: {str(e)}", exc_info=True)

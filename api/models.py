from pydantic import BaseModel
from typing import Dict, Optional


class Book(BaseModel):
    """
    Modelo Pydantic para representar um livro.
    """

    id: int
    title: str
    href: str
    price: float
    rating: int
    availability: str
    category: str
    image_url: str


class Token(BaseModel):
    """
    Modelo para resposta de token JWT.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Modelo para dados contidos no token JWT.
    """

    username: str
    jti: str


class User(BaseModel):
    """
    Modelo para usuário de autenticação.
    """

    username: str
    password: Optional[str] = None


class PredictionInput(BaseModel):
    """
    Modelo para entrada de predições de ML.
    """

    features: Dict[str, float]

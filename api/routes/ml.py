from fastapi import APIRouter, Depends
from api.models import PredictionInput
from api.dependencies import get_books_data
import pandas as pd
import logging

# Reutiliza o logger definido em main.py
logger = logging.getLogger("api_logger")

router = APIRouter(prefix="/api/v1/ml", tags=["ml"])


@router.get("/features")
async def get_ml_features(df: pd.DataFrame = Depends(get_books_data)):
    """
    Retorna dados formatados para features de ML (ex.: preço, rating, dummy variables para categoria).
    """
    features = df[["price", "rating", "category"]].copy()
    features = pd.get_dummies(features, columns=["category"], prefix="category")
    logger.info("Features para ML retornadas")
    return features.to_dict("records")


@router.get("/training-data")
async def get_training_data(df: pd.DataFrame = Depends(get_books_data)):
    """
    Retorna dataset completo para treinamento de ML.
    """
    logger.info("Dataset de treinamento retornado")
    return df.to_dict("records")


@router.post("/predictions")
async def make_predictions():
    """
    Recebe features e retorna predições (apenas um mock).
    """
    logger.info(f"Predições solicitadas")
    # Mock: retorna a soma dos valores das features como predição
    return {"prediction": "it's a simple example"}

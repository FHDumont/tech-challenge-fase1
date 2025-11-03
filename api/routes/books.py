from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from api.models import Book
from api.dependencies import get_books_data, get_current_user
import pandas as pd
import logging

# Reutiliza o logger definido em main.py
logger = logging.getLogger("api_logger")

router = APIRouter(prefix="/api/v1", tags=["books"])


@router.get("/books", response_model=List[Book])
async def get_all_books(df: pd.DataFrame = Depends(get_books_data)):
    """
    Lista todos os livros disponíveis na base de dados.
    """
    logger.debug("Listando todos os livros")
    return df.to_dict("records")


@router.get("/books/search", response_model=List[Book])
async def search_books(title: str = None, category: str = None, df: pd.DataFrame = Depends(get_books_data)):
    """
    Busca livros por título, categoria ou ambos. Pelo menos um parâmetro deve ser fornecido.
    """
    if not title and not category:
        logger.error("Busca inválida: nenhum parâmetro (title ou category) fornecido")
        raise HTTPException(status_code=400, detail="Pelo menos um parâmetro (title ou category) deve ser fornecido")

    result = df
    if title:
        result = result[result["title"].str.contains(title, case=False, na=False)]
    if category:
        result = result[result["category"].str.contains(category, case=False, na=False)]

    logger.debug(f"Busca realizada - Título: {title}, Categoria: {category}, Resultados: {len(result)}")
    return result.to_dict("records")


@router.get("/categories")
async def get_categories(df: pd.DataFrame = Depends(get_books_data)):
    """
    Lista todas as categorias de livros disponíveis.
    """
    categories = df["category"].unique().tolist()
    logger.debug(f"Listando {len(categories)} categorias")
    return {"categories": categories}


@router.get("/health")
async def health_check(df: pd.DataFrame = Depends(get_books_data)):
    """
    Verifica o status da API e conectividade com os dados.
    """
    status = {"api_status": "healthy", "data_loaded": not df.empty}
    logger.debug("Verificação de saúde da API realizada")
    return status


@router.get("/stats/overview")
async def get_stats_overview(df: pd.DataFrame = Depends(get_books_data)):
    """
    Retorna estatísticas gerais da coleção.
    """
    stats = {
        "total_books": len(df),
        "average_price": float(df["price"].mean()) if not df.empty else 0.0,
        "rating_distribution": df["rating"].value_counts().to_dict(),
    }
    logger.debug("Estatísticas gerais retornadas")
    return stats


@router.get("/stats/categories")
async def get_stats_categories(df: pd.DataFrame = Depends(get_books_data)):
    """
    Retorna estatísticas detalhadas por categoria (quantidade de livros e preços).
    """
    try:
        stats = df.groupby("category").agg({"title": "count", "price": ["mean", "min", "max"]}).reset_index()
        stats.columns = ["category", "total_books", "avg_price", "min_price", "max_price"]
        stats_dict = stats.to_dict("records")
        logger.debug("Estatísticas por categoria retornadas")
        return stats_dict
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas por categoria: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao calcular estatísticas por categoria")


@router.get("/books/top-rated", response_model=List[Book])
async def get_top_rated_books(df: pd.DataFrame = Depends(get_books_data)):
    """
    Lista os livros com a melhor avaliação (rating 5).
    """
    try:
        top_rated = df[df["rating"] == 5]
        if top_rated.empty:
            logger.info("Nenhum livro com rating 5 encontrado")
            return []
        logger.debug(f"Retornados {len(top_rated)} livros com rating 5")
        return top_rated.to_dict("records")
    except Exception as e:
        logger.error(f"Erro ao buscar livros top-rated: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao buscar livros top-rated")


@router.get("/books/price-range", response_model=List[Book])
async def get_books_by_price_range(min_price: float = 0.0, max_price: float = float("inf"), df: pd.DataFrame = Depends(get_books_data)):
    """
    Filtra livros dentro de uma faixa de preço específica.
    """
    if min_price < 0:
        logger.error(f"Parâmetro min_price inválido: {min_price} (deve ser não-negativo)")
        raise HTTPException(status_code=400, detail="min_price deve ser não-negativo")
    if max_price < min_price:
        logger.error(f"Parâmetro max_price inválido: {max_price} (deve ser maior ou igual a min_price)")
        raise HTTPException(status_code=400, detail="max_price deve ser maior ou igual a min_price")

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    filtered = df[(df["price"] >= min_price) & (df["price"] <= max_price) & (df["price"].notna())]

    logger.debug(f"Filtrados {len(filtered)} livros na faixa de preço {min_price} a {max_price}")
    return filtered.to_dict("records")


@router.get("/books/{book_id}", response_model=Book)
async def get_book_by_id(book_id: int, df: pd.DataFrame = Depends(get_books_data)):
    """
    Retorna detalhes de um livro específico pelo ID (inteiro).
    """
    book = df[df["id"] == book_id]
    if book.empty:
        logger.error(f"Livro com ID {book_id} não encontrado")
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    logger.debug(f"Retornado livro com ID {book_id}")
    return book.iloc[0].to_dict()

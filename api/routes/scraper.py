from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from api.models import Book
from api.dependencies import get_books_data, get_current_user
import pandas as pd
import logging
from api.scrapper.bookScraper import BookScraper
from api.dependencies import load_books_data
import csv

# Reutiliza o logger definido em main.py
logger = logging.getLogger("api_logger")

router = APIRouter(prefix="/api/v1", tags=["scraper"])


@router.post("/scraping/trigger")
async def trigger_scraping(current_user: dict = Depends(get_current_user)):
    """
    Endpoint protegido para disparar o scraping (admin apenas).
    """
    try:
        scraper = BookScraper()
        books = scraper.scrape_all()

        if not books:
            logger.error("Nenhum livro extraído durante o scraping")
            raise HTTPException(status_code=500, detail="Nenhum livro extraído durante o scraping")

        with open("data/books.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["id", "title", "href", "price", "rating", "availability", "category", "image_url"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(books)

        logger.info(f"Scraping concluído: {len(books)} livros salvos")

        # Recarrega o novo csv para não precisar reiniciar a aplicação
        load_books_data()

        return {"message": f"{len(books)} livros extraídos e salvos"}

    except HTTPException as e:
        logger.error(f"Erro ao executar scraping: {str(e)}", exc_info=True)
        raise e

    except Exception as e:
        logger.error(f"Erro ao executar scraping: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao executar o scraping")

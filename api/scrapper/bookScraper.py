import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import logging
from urllib.parse import urljoin
import hashlib

logger = logging.getLogger("scraper_logger")
logger.setLevel(logging.INFO)

info_handler = logging.FileHandler("logs/scrapper.log")
info_handler.setLevel(logging.INFO)
info_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
info_handler.setFormatter(info_formatter)
logger.addHandler(info_handler)

error_handler = logging.FileHandler("logs/scrapper-error.log")
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
error_handler.setFormatter(error_formatter)
logger.addHandler(error_handler)


class BookScraper:
    """
    Classe para realizar web scraping no site https://books.toscrape.com/.
    Otimizada com sessão de requests para reutilização de conexões e threading para paralelismo em categorias.
    """

    def __init__(self):
        """
        Inicializa o scraper com uma sessão de requests para otimizar performance em múltiplas requisições
        """
        self.session = requests.Session()
        self.base_url = "https://books.toscrape.com/"

        # O rating será convertido para inteiro para facilitar pesquisas posteriores
        self.RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

    def clean_price(self, valor: str) -> float:
        """
        Limpa o valor de preço removendo caracteres não numéricos e convertendo para float.
        Trata vírgulas como separadores decimais se necessário.
        """
        try:
            # Remove tudo que não seja dígito, vírgula ou ponto
            valor_limpo = re.sub(r"[^0-9,\.]", "", valor)
            # Substitui vírgula por ponto (caso seja separador decimal)
            if "," in valor_limpo and "." not in valor_limpo:
                valor_limpo = valor_limpo.replace(",", ".")
            return float(valor_limpo)
        except ValueError as e:
            logger.error(f"Erro ao converter preço '{valor}': {str(e)}", exc_info=True)
            return 0.0  # Retorna 0.0 em caso de erro na conversão

    def get_categories(self):
        """
        Obtém a lista de categorias do site, com nomes e URLs associadas.
        Retorna um dicionário {categoria: url}.
        """
        try:
            logger.info(f"Iniciando pesquisa de categorias")
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")  # Usa lxml para parsing mais rápido.

            categories = {}
            for link in soup.select("div.side_categories ul.nav-list li ul li a"):
                category_name = link.text.strip()
                category_url = self.base_url + link["href"]
                categories[category_name] = category_url

            logger.info(f"Total de categorias encontradas [{len(categories)}]")
            return categories
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.error(f"Erro ao obter categorias: {str(e)}", exc_info=True)
            logger.info(f"Erro ao obter categorias. Verifique o arquivo scraper.log para detalhes.")
            return {}

    def scrape_category(self, category_name, category_url):
        """
        Copia todos os livros de uma categoria específica, paginando até o final.
        Retorna uma lista de dicionários com dados dos livros.
        Otimizado para parar ao detectar ausência de próxima página.
        """
        books = []
        page = 1
        while True:
            try:
                if page > 1:
                    page_url = category_url.replace("index.html", f"page-{page}.html")
                else:
                    page_url = category_url

                response = self.session.get(page_url, timeout=10)
                if response.status_code != 200:
                    break
                soup = BeautifulSoup(response.text, "lxml")

                for article in soup.select("ol.row li article.product_pod"):
                    try:
                        # Extrai dados da página da categoria
                        title = article.h3.a["title"]
                        price = article.select_one("p.price_color").text.strip()
                        price_only = self.clean_price(price)
                        rating = self.RATING_MAP.get(article.p["class"][1], 0)  # Extrai de 'star-rating X' -> 'X'
                        availability = article.select_one("p.availability").text.strip()
                        image_src = article.img["src"].replace("../", "")
                        image_url = self.base_url + image_src
                        book_url = urljoin(self.base_url, article.h3.a["href"].replace("../../../", "catalogue/"))

                        # Gerar ID único baseado em hash
                        unique_str = f"{title}_{category_name}"
                        book_id = int(hashlib.md5(unique_str.encode()).hexdigest(), 16) % (10**8)

                        books.append(
                            {
                                "id": book_id,
                                "title": title,
                                "href": book_url,
                                "price": price_only,
                                "rating": rating,
                                "availability": availability,
                                "category": category_name,
                                "image_url": image_url,
                            }
                        )
                    except (requests.exceptions.RequestException, AttributeError) as e:
                        logger.error(f"Erro ao raspar livro na categoria {category_name}, página {page}: {str(e)}", exc_info=True)
                        continue

                if not soup.select_one("li.next"):
                    break
                page += 1

            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao acessar página {page} da categoria {category_name}: {str(e)}", exc_info=True)
                break

        logger.info(f"{len(books)} livros encontrados na categoria {category_name} e url {category_url}")
        return books

    def scrape_all(self):
        """
        Copia todos os livros de todas as categorias em paralelo usando threading.
        Retorna uma lista consolidada de todos os livros.
        Otimizado com ThreadPoolExecutor para processar categorias simultaneamente (máx. 10 workers para evitar sobrecarga no servidor).
        """
        try:
            categories = self.get_categories()
            if not categories:
                return []

            all_books = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(self.scrape_category, name, url) for name, url in categories.items()]
                for future in as_completed(futures):
                    try:
                        all_books.extend(future.result())
                    except Exception as e:
                        logger.error(f"Erro ao processar categoria: {str(e)}", exc_info=True)

            logger.info(f"Total de {len(all_books)} livros encontrados")
            return all_books
        except Exception as e:
            logger.error(f"Erro geral no scraping: {str(e)}", exc_info=True)
            return []

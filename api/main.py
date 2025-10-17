from fastapi import FastAPI, Request
from fastapi.responses import Response
from api.routes import books, auth, ml, scraper
import logging
import time

# Configuração de logging com dois arquivos: api.log (INFO) e api-error.log (ERROR)
logger = logging.getLogger("api_logger")
logger.setLevel(logging.INFO)

info_handler = logging.FileHandler("logs/api.log")
info_handler.setLevel(logging.INFO)
info_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
info_handler.setFormatter(info_formatter)
logger.addHandler(info_handler)

error_handler = logging.FileHandler("logs/api-error.log")
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
error_handler.setFormatter(error_formatter)
logger.addHandler(error_handler)

# Configuração de loggin com visão de monitoramento (estilo http server)
logger_http = logging.getLogger("http_logger")
logger_http.setLevel(logging.INFO)
http_handler = logging.FileHandler("logs/http.log")
logger_http.addHandler(http_handler)

app = FastAPI(title="Books Scraper API", version="1.0.0")


# Middleware para logar todas as requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time

    # Dados semelhantes aos logs do Apache/Nginx
    client_ip = request.client.host
    method = request.method
    url = str(request.url)
    status_code = response.status_code
    user_agent = request.headers.get("user-agent", "-")

    log_message = f'{client_ip} "{method} {url} HTTP/1.1" {status_code} "{user_agent}" {process_time:.2f}s'

    if status_code >= 400:
        logger_http.error(log_message)
    else:
        logger_http.info(log_message)

    return response


# Inclui os roteadores
app.include_router(books.router)
app.include_router(auth.router)
app.include_router(ml.router)
app.include_router(scraper.router)


@app.on_event("startup")
async def startup_event():
    """
    Evento de inicialização da API.
    """
    logger.info("API iniciada")

from fastapi import Request, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from api.models import Token, User
from api.dependencies import create_access_token, verify_password, fake_users_db, revoke_token, oauth2_scheme, get_current_user, SECRET_KEY
import logging
from jose import jwt

# Reutiliza o logger definido em main.py
logger = logging.getLogger("api_logger")

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint para autenticação e obtenção de token JWT.
    """
    logger.info(f"Tentativa de login para usuário: {form_data.username}")
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        logger.error(f"Falha na autenticação para usuário: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    logger.info(f"Login bem-sucedido para usuário: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Endpoint para renovar o token JWT. Revoga o token anterior.
    """
    logger.info(f"Renovação de token para usuário: {current_user['username']}")
    try:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Token inválido")
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        jti = payload.get("jti")
        if jti:
            revoke_token(jti)
        access_token = create_access_token(data={"sub": current_user["username"]})
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        logger.error(f"Erro ao renovar token para usuário {current_user['username']}: {str(e)}", exc_info=True)
        raise e
    except Exception as e:
        logger.error(f"Erro ao renovar token para usuário {current_user['username']}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro ao renovar o token")

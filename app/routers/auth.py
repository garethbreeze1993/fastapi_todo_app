from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import exc
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app import oauth2
from app.schemas import AccessToken, Token, RefreshToken
from app.utils import verify_password

router = APIRouter(tags=["Authentication"])


@router.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db_session: Session = Depends(get_db)):

    try:
        user = db_session.query(models.User)\
            .filter(models.User.email == form_data.username)\
            .one()
    except exc.SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(plain_password=form_data.password, hashed_password=user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # create token and return it
    access_token = oauth2.create_access_token(data=dict(user_id=user.id))
    refresh_token = oauth2.create_refresh_token(data=dict(user_id=user.id))
    return {'access_token': access_token, "token_type": "bearer", "refresh_token": refresh_token}


@router.post('/refresh', response_model=AccessToken)
def refresh(token: RefreshToken):
    credentials_exception = HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials',
                                          headers={"WWW-AUTHENTICATE": "BEARER"})

    user_id = oauth2.verify_refresh_token(token=token.refresh_token, credentials_exception=credentials_exception)
    access_token = oauth2.create_access_token(data=dict(user_id=user_id))
    return {'access_token': access_token, "token_type": "bearer"}

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import exc
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app import oauth2
from app.schemas import Token
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
    access_token = oauth2.create_access_token(data=dict(sub=user.id))
    return {'access_token': access_token, "token_type": "bearer"}

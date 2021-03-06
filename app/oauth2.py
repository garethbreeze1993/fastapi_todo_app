from datetime import datetime, timedelta

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import TokenData

SECRET_KEY = "d6872f3de23291558ff27dd0986df296b0bede71ab2d31dac334822d29a882d1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# To get a token sends a request with username and password to api_root/login


def create_access_token(data: dict):
    to_encode = data.copy()
    expiry_datetime = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expiry_datetime})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get('user_id')
        if user_id is None:
            raise credentials_exception

        token_data = TokenData(user_id=user_id)

    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db_session: Session = Depends(get_db)):
    credentials_exception = HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials',
                                          headers={"WWW-AUTHENTICATE": "BEARER"})

    token = verify_access_token(token=token, credentials_exception=credentials_exception)

    user = db_session.query(models.User)\
        .get(token.user_id)

    return user

from jose import jwt
import pytest

from app.oauth2 import SECRET_KEY, ALGORITHM
from app.schemas import UserResponse, Token, AccessToken


def test_create_user(client):
    res = client.post('/users/', json={"email": "test_create@gmail.com", "password": "password123"})
    new_user = UserResponse(**res.json())
    assert new_user.email == "test_create@gmail.com"
    assert res.status_code == 201


def test_login(client, test_user):
    res = client.post('/login', {'username': test_user['email'], 'password': test_user['password']})
    login_res = Token(**res.json())
    payload = jwt.decode(login_res.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get('user_id')
    assert res.status_code == 200
    assert user_id == test_user['id']
    assert login_res.token_type == 'bearer'
    assert login_res.refresh_token


@pytest.mark.parametrize("email, password, status_code",
                         [('wrong_email@gmail.com', 'password123', 401),
                          ('wrong_email@gmail.com', 'wrongpassword123', 401),
                          ('gareth@gmail.com', 'wrongpassword123', 401),
                          (None, 'password123', 422),
                          ('gareth@gmail.com', None, 422)])
def test_incorrect_login(client, test_user, email, password, status_code):
    res = client.post('/login', {'username': email, 'password': password})
    assert res.status_code == status_code


def test_get_new_access_token_from_refresh(authorised_client, refresh_token, test_user):
    res = authorised_client.post('/refresh', json={'refresh_token': refresh_token})
    new_cred_res = AccessToken(**res.json())
    payload = jwt.decode(new_cred_res.access_token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get('user_id')
    assert res.status_code == 200
    assert user_id == test_user['id']
    assert new_cred_res.token_type == 'bearer'

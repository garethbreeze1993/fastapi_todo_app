from fastapi.testclient import TestClient
import pytest

from app import models
from app.database import Base, get_db
from app.main import app
from app.oauth2 import create_access_token, create_refresh_token
from tests.database import TestingSessionLocal, engine


@pytest.fixture
def get_test_db_session():
    """
    From the test database yield a SQLAlchemy db session
    :return:
    """
    Base.metadata.drop_all(bind=engine)  # Drop tables from test database if any
    Base.metadata.create_all(bind=engine)  # Create tables for test database
    db_session = TestingSessionLocal()  # create a dbsession from test database
    try:
        # Request and response delivered during yield statement allowing functions access to db session
        yield db_session
    finally:
        # After response close the db session
        db_session.close()


@pytest.fixture
def client(get_test_db_session):
    """
    Making a test client to run our tests from
    :param get_test_db_session: The pycharm fixture which is a SQLAlchemy db session
    :return:
    """

    def override_get_db():
        try:
            yield get_test_db_session
        finally:
            get_test_db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture
def test_user(client) -> dict:
    """
    Saves a user to the database and returns the dict so we have information from that user
    :param client: A pycharm fixture which is a fastapi test client
    :return: dict with user information
    """
    user_dict = {'email': 'gareth@gmail.com', 'password': 'password123'}
    res = client.post('/users/', json=user_dict)
    assert res.status_code == 201
    new_user = dict(password=user_dict['password'], **res.json())
    return new_user


@pytest.fixture
def test_user_2(client) -> dict:
    """
    Saves a user to the database and returns the dict so we have information from that user
    :param client: A pycharm fixture which is a fastapi test client
    :return: dict with user information
    """
    user_dict = {'email': 'jack@gmail.com', 'password': 'password1234'}
    res = client.post('/users/', json=user_dict)
    assert res.status_code == 201
    new_user = dict(password=user_dict['password'], **res.json())
    return new_user


@pytest.fixture
def token(test_user):
    """
    Gives us a JWT token so we can have an authorised user for testing purposes
    :param test_user: Pycharm fixture which creates a user and returns a dict with user information
    :return:
    """
    access_token = create_access_token(data=dict(user_id=test_user['id']))
    return access_token


@pytest.fixture
def authorised_client(client, token):
    """
    Gives us an authorised client which can be used to test endpoints which need a user to be logged in
    :param client: FastApi test client
    :param token: A JWT bearer token used for authorization
    :return:
    """
    client.headers.update({'Authorization': f'Bearer {token}'})
    return client


@pytest.fixture
def token_2(test_user_2):
    """
    Gives us a JWT token so we can have an authorised user for testing purposes
    :param test_user_2: Pycharm fixture which creates a user and returns a dict with user information
    :return:
    """
    access_token = create_access_token(data=dict(user_id=test_user_2['id']))
    return access_token


@pytest.fixture
def authorised_client_2(client, token_2):
    """
    Gives us an authorised client which can be used to test endpoints which need a user to be logged in
    :param client: FastApi test client
    :param token_2: A JWT bearer token used for authorization
    :return:
    """
    client.headers.update({'Authorization': f'Bearer {token_2}'})
    return client


@pytest.fixture
def create_test_tasks(test_user, get_test_db_session, test_user_2):
    test_tasks = [{'title': 'Task 1', 'description': 'Description 1', 'owner_id': test_user['id'],
                   'deadline': '2022-08-31', 'completed': True},
                  {'title': 'Task 2', 'description': 'Description 2', 'owner_id': test_user['id'], 'deadline': None,
                   'completed': False},
                  {'title': 'Task 3', 'description': 'Description 3', 'owner_id': test_user['id'],
                   'deadline': '2022-08-31'},
                  {'title': 'Task 4', 'description': 'Description 4', 'owner_id': test_user_2['id'],
                   'deadline': '2022-08-31', 'completed': True},
                  {'title': 'Task 5', 'description': 'Description 5', 'owner_id': test_user_2['id'], 'deadline': None}]

    for task in test_tasks:
        model_task = models.Task(**task)
        get_test_db_session.add(model_task)

    get_test_db_session.commit()

    task_query = get_test_db_session.query(models.Task) \
        .all()

    return task_query


@pytest.fixture
def refresh_token(test_user):
    """
    Gives us a JWT refresh token so we can test the refersh token functionality
    :param test_user: Pycharm fixture which creates a user and returns a dict with user information
    :return:
    """
    refresh_token = create_refresh_token(data=dict(user_id=test_user['id']))
    return refresh_token

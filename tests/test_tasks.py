import pytest
from app.schemas import TaskResponse


def test_user_1_get_all_tasks(authorised_client, create_test_tasks):
    res = authorised_client.get('/tasks')
    assert res.status_code == 200
    assert res.json()['total'] == 3


def test_user_2_get_all_tasks(authorised_client_2, create_test_tasks):
    res = authorised_client_2.get('/tasks')
    assert res.status_code == 200
    assert res.json()['total'] == 2


def test_unauthorised_user_get_all_tasks(client, create_test_tasks):
    res = client.get('/tasks')
    assert res.status_code == 401


@pytest.mark.parametrize("id_, status_code", [(1, 200), (2, 200), (3, 200), (4, 404), (5, 404)])
def test_task_detail_test_user_1(authorised_client, create_test_tasks, id_, status_code):
    res = authorised_client.get(f'/tasks/{id_}')
    assert res.status_code == status_code
    if status_code == 200:
        task_response = TaskResponse(**res.json())
        assert task_response.id == create_test_tasks[id_ - 1].id
        assert task_response.title == create_test_tasks[id_ - 1].title
        assert task_response.description == create_test_tasks[id_ - 1].description
        assert task_response.completed == create_test_tasks[id_ - 1].completed
        assert task_response.owner_id == create_test_tasks[id_ - 1].owner_id
    elif status_code == 404:
        assert res.json().get("detail") == f'Task not found with id={id_}'


@pytest.mark.parametrize("id_, status_code", [(1, 404), (2, 404), (3, 404), (4, 200), (5, 200)])
def test_task_detail_test_user_2(authorised_client_2, create_test_tasks, id_, status_code):
    res = authorised_client_2.get(f'/tasks/{id_}')
    assert res.status_code == status_code
    if status_code == 200:
        task_response = TaskResponse(**res.json())
        assert task_response.id == create_test_tasks[id_ - 1].id
        assert task_response.title == create_test_tasks[id_ - 1].title
        assert task_response.description == create_test_tasks[id_ - 1].description
        assert task_response.completed == create_test_tasks[id_ - 1].completed
        assert task_response.owner_id == create_test_tasks[id_ - 1].owner_id
    elif status_code == 404:
        assert res.json().get("detail") == f'Task not found with id={id_}'


def test_unauthorized_user_task_detail(client, create_test_tasks):
    res = client.get(f'/tasks/{create_test_tasks[0].id}')
    assert res.status_code == 401


def test_authorized_user_task_not_exist(authorised_client, create_test_tasks):
    id_ = 4444
    res = authorised_client.get(f'/tasks/{id_}')
    assert res.status_code == 404
    assert res.json().get("detail") == f'Task not found with id={id_}'

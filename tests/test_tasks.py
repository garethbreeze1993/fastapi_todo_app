from datetime import datetime
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


def test_create_task_test_user_1_deadline_set(authorised_client, test_user):
    form_data = {"title": "title1", "description": "description1", "deadline": "2022-04-24"}
    res = authorised_client.post("/tasks/", json=form_data)
    task_response = TaskResponse(**res.json())
    assert res.status_code == 201
    assert task_response.title == form_data['title']
    assert task_response.description == form_data['description']
    assert task_response.deadline == datetime.strptime(form_data['deadline'], '%Y-%m-%d').date()
    assert task_response.owner_id == test_user.get('id')
    assert task_response.completed is False


def test_create_task_test_user_1_deadline_not_set(authorised_client, test_user):
    form_data = {"title": "title1", "description": "description1"}
    res = authorised_client.post("/tasks/", json=form_data)
    task_response = TaskResponse(**res.json())
    assert res.status_code == 201
    assert task_response.title == form_data['title']
    assert task_response.description == form_data['description']
    assert task_response.deadline is None
    assert task_response.owner_id == test_user.get('id')
    assert task_response.completed is False


def test_unauthorised_client_create_task(client):
    form_data = {"title": "title1", "description": "description1"}
    res = client.post("/tasks/", json=form_data)
    assert res.status_code == 401


def test_authorized_user_delete_own_post_success(authorised_client, create_test_tasks):
    res = authorised_client.delete(f'/tasks/{create_test_tasks[0].id}')
    assert res.status_code == 204


def test_authorized_user_2_delete_not_own_post_failure(authorised_client_2, create_test_tasks):
    res = authorised_client_2.delete(f'/tasks/{create_test_tasks[0].id}')
    assert res.status_code == 403
    assert res.json().get("detail") == 'Not authorised to perform requested action'


def test_authorized_user_delete_post_not_exist(authorised_client, create_test_tasks):
    id_ = 4444
    res = authorised_client.delete(f'/tasks/{id_}')
    assert res.status_code == 404


def test_unauthorized_user_delete_post_failure(client, create_test_tasks):
    res = client.delete(f'/tasks/{create_test_tasks[0].id}')
    assert res.status_code == 401


def test_complete_task_success(authorised_client, create_test_tasks):
    assert create_test_tasks[1].completed is False
    res = authorised_client.put(f'/tasks/complete/{create_test_tasks[1].id}', json={"completed": True})
    assert res.status_code == 200
    task_response = TaskResponse(**res.json())
    assert task_response.id == create_test_tasks[1].id
    assert task_response.completed is True


def test_complete_task_not_owner_task_failure(authorised_client_2, create_test_tasks):
    res = authorised_client_2.put(f'/tasks/complete/{create_test_tasks[1].id}', json={"completed": True})
    assert res.status_code == 403
    assert res.json().get("detail") == 'Not authorised to perform requested action'


def test_complete_task_not_exist(authorised_client, create_test_tasks):
    id_ = 4444
    res = authorised_client.put(f'/tasks/complete/{id_}', json={"completed": True})
    assert res.status_code == 404
    assert res.json().get("detail") == f'Task not found id={id_}'


def test_unauthorised_client_complete_post(client, create_test_tasks):
    res = client.put(f'/tasks/complete/{create_test_tasks[1].id}', json={"completed": True})
    assert res.status_code == 401


def test_update_task_success_deadline_set(authorised_client, create_test_tasks, test_user):
    form_data = {"title": "changedtitle1", "description": "changeddescription1", "deadline": "2022-04-11"}
    res = authorised_client.put(f'/tasks/{create_test_tasks[0].id}', json=form_data)
    assert res.status_code == 200
    task_response = TaskResponse(**res.json())
    assert task_response.id == create_test_tasks[0].id
    assert task_response.title == form_data['title']
    assert task_response.description == form_data['description']
    assert task_response.owner_id == test_user.get('id')
    assert task_response.deadline == datetime.strptime(form_data['deadline'], '%Y-%m-%d').date()


def test_update_task_success_deadline_not_passed_in(authorised_client, create_test_tasks, test_user):
    form_data = {"title": "changedtitle1", "description": "changeddescription1"}
    res = authorised_client.put(f'/tasks/{create_test_tasks[0].id}', json=form_data)
    assert res.status_code == 200
    task_response = TaskResponse(**res.json())
    assert task_response.id == create_test_tasks[0].id
    assert task_response.title == form_data['title']
    assert task_response.description == form_data['description']
    assert task_response.owner_id == test_user.get('id')
    assert task_response.deadline is None


def test_update_task_not_owner_task_failure(authorised_client_2, create_test_tasks):
    form_data = {"title": "changedtitle1", "description": "changeddescription1"}
    res = authorised_client_2.put(f'/tasks/{create_test_tasks[0].id}', json=form_data)
    assert res.status_code == 403
    assert res.json().get("detail") == 'Not authorised to perform requested action'


def test_update_task_not_exist(authorised_client, create_test_tasks):
    form_data = {"title": "changedtitle1", "description": "changeddescription1"}
    id_ = 4444
    res = authorised_client.put(f'/tasks/{id_}', json=form_data)
    assert res.status_code == 404
    assert res.json().get("detail") == f'Task not found id={id_}'


def test_unauthorised_user_update_task_failure(client, create_test_tasks, test_user):
    form_data = {"title": "changedtitle1", "description": "changeddescription1", "deadline": "2022-04-11"}
    res = client.put(f'/tasks/{create_test_tasks[0].id}', json=form_data)
    assert res.status_code == 401

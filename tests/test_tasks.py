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

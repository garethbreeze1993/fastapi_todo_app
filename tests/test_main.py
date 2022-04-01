def test_root_authorised_client(authorised_client):
    res = authorised_client.get('/')
    assert res.status_code == 200
    assert res.json() == {"Hello": 'World'}


def test_root_unauthorised_client(client):
    res = client.get('/')
    assert res.status_code == 401

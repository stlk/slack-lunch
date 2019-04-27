import os
import pytest
from flask import json
from server import create_app


@pytest.fixture
def app(request):
    config = {"TESTING": True, "DEBUG": True}

    app = create_app(config=config)

    with app.app_context():
        yield app


@pytest.fixture
def client(request, app):
    client = app.test_client()
    return client


def test_zomato_returned(client):
    rv = client.post(
        "/slash", data={"text": "jiriho z podebrad, prague", "response_url": "test"}
    )
    assert rv.status == "200 OK"

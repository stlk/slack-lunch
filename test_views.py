import os
import pytest
from flask import json
import slash.index
import lookup.index


@pytest.fixture
def slash_app(request):
    config = {"TESTING": True, "DEBUG": True}
    app = slash.index.app
    app.config.update(config or {})

    with app.app_context():
        yield app


def test_slash(slash_app):
    client = slash_app.test_client()
    rv = client.post(
        "/slash",
        data={
            "text": "jiriho z podebrad, prague",
            "response_url": "http://example.com/",
        },
    )
    assert rv.status == "200 OK"


@pytest.fixture
def lookup_app(request):
    config = {"TESTING": True, "DEBUG": True}
    app = lookup.index.app
    app.config.update(config or {})

    with app.app_context():
        yield app


def test_lookup(lookup_app):
    client = lookup_app.test_client()
    rv = client.post(
        "/lookup",
        json={
            "location": "Šaldova, 186 00 Prague, Czechia",
            "lat": 50.0954784,
            "lng": 14.4544032,
            "response_url": "http://example.com/",
        },
    )
    assert rv.status == "200 OK"

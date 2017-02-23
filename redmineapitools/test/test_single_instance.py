"""
    :copyright: (c) 2017 by Tobias `dpausp` <dpausp@posteo.de>
    :license: BSD, see LICENSE for more details.
"""
import json
import pytest
jdumps = json.dumps
from os import path
pjoin = path.join

import httpretty
from httpretty import register_uri
from pytest import fixture, yield_fixture
from redmineapitools.single_instance import RedmineAPIWrapper
import yaml

BASEDIR = path.join(path.dirname(__file__), "data")
REDMINE_URI = "http://localhost:3000"


def redmine_uri(path):
    return pjoin(REDMINE_URI, path)


def load_yaml_test_data(name):
    filepath = path.join(BASEDIR, name + ".yml")
    with open(filepath) as f:
        return yaml.load(f)


@fixture
def redmine():
    return RedmineAPIWrapper(REDMINE_URI)


@fixture
def fake_custom_fields():
    custom_fields = load_yaml_test_data("custom_fields")
    register_uri(httpretty.GET,
                 redmine_uri("custom_fields.json?limit=100&offset=0"),
                 body=jdumps(custom_fields),
                 content_type="application/json")
    return custom_fields


@fixture
def fake_status():
    statuses = load_yaml_test_data("statuses")
    register_uri(httpretty.GET,
                 redmine_uri("issue_statuses.json?limit=100&offset=0"),
                 body=jdumps(statuses),
                 content_type="application/json")
    return statuses


@fixture
def fake_trackers():
    trackers = load_yaml_test_data("trackers")
    register_uri(httpretty.GET,
                 redmine_uri("trackers.json?limit=100&offset=0"),
                 body=jdumps(trackers),
                 content_type="application/json")
    return trackers


@pytest.mark.httpretty
def test_custom_fields(redmine, fake_custom_fields):
    custom_fields = [cf._attributes for cf in redmine.custom_fields]
    assert fake_custom_fields == {"custom_fields": custom_fields}


@pytest.mark.httpretty
def test_statuses(redmine, fake_status):
    status = [{k: v for k, v in cf._attributes.items() if k !="issues"} for cf in redmine.issue_status]
    assert fake_status == {"issue_statuses": status}


@pytest.mark.httpretty
def test_trackers(redmine, fake_trackers):
    trackers = [{k: v for k, v in cf._attributes.items() if k !="issues"} for cf in redmine.trackers]
    assert fake_trackers == {"trackers": trackers}

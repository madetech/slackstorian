import pytest
import uuid

from slackstorian.backup_slack import get_env


def test_eng_throws_an_exception_if_not_set():
    with pytest.raises(Exception):
        get_env('test')


def test_eng_throws_an_exception_if_not_set(monkeypatch):
    env_var_name = str(uuid.uuid4())
    env_var_value = str(uuid.uuid4())

    monkeypatch.setenv(env_var_name, env_var_value)

    assert get_env(env_var_name) == env_var_value

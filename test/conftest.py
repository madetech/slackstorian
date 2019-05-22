import pytest
import responses


@pytest.fixture
def mocked_response():
    with responses.RequestsMock() as rsps:
        yield rsps

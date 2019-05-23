import pytest

from slackstorian.slack_client import SlackClient, AuthenticationError


def test_client_throws_an_exception_if_not_set():
    with pytest.raises(AuthenticationError):
        SlackClient('BANG!')


def test_can_download_list_of_usernames(mocked_response):
    mocked_response.add(mocked_response.GET, 'https://slack.com/api/auth.test?token=test+fake+token', json={"ok": True},
                        status=200)

    mocked_response.add(
        mocked_response.GET, 'https://slack.com/api/users.list?presence=0&token=test+fake+token',
        json={
            "ok": True,
            "members": [
                {"name": "Cormac"},
                {"name": "el"}
            ]
        },
        status=200
    )

    client = SlackClient('test fake token')

    expected_response = '''[
  {
    "name": "Cormac"
  },
  {
    "name": "el"
  }
]'''
    assert client.user_data_json() == expected_response


def test_can_download_channels_list(mocked_response):
    mocked_response.add(mocked_response.GET, 'https://slack.com/api/auth.test?token=test+fake+token', json={"ok": True},
                        status=200)

    mocked_response.add(
        mocked_response.GET, 'https://slack.com/api/channels.list?token=test+fake+token',
        json={
            "ok": True,
            "channels": [
                {
                    "id": "C0G9QF9GW",
                    "name": "random",
                    "is_channel": True,
                }
            ]
        },
        status=200
    )

    client = SlackClient('test fake token')

    expected_response = '''[
  {
    "id": "C0G9QF9GW",
    "is_channel": true,
    "name": "random"
  }
]'''

    assert client.channels().as_json() == expected_response


def test_can_download_channels_history(mocked_response):
    mocked_response.add(mocked_response.GET, 'https://slack.com/api/auth.test?token=test+fake+token', json={"ok": True},
                        status=200)

    mocked_response.add(
        mocked_response.GET,
        'https://slack.com/api/channels.history?channel=fake_channel&oldest=0&count=1000&inclusive=0&unreads=0&token=test+fake+token',
        json={
            "ok": True,
            "messages": [
                {"is_message": True}
            ]
        },
        status=200
    )

    client = SlackClient('test fake token')

    assert client.channel_history({"id": "fake_channel"}) == '''[
  {
    "is_message": true
  }
]'''


def test_can_post_to_channel(mocked_response):
    mocked_response.add(mocked_response.GET, 'https://slack.com/api/auth.test?token=test+fake+token', json={"ok": True},
                        status=200)

    mocked_response.add(mocked_response.POST, 'https://slack.com/api/chat.postMessage?token=test+fake+token',
                        json={
                            "ok": True,
                        },
                        status=200)

    client = SlackClient('test fake token')

    assert client.post_to_channel('test_channel', 'hey testers!').successful

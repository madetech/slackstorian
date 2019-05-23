from unittest.mock import Mock, call

from slackstorian import run_backup
from slackstorian.slack_client import Channels


def test_usernames_are_backed_up():
    mock_slack = Mock()
    mock_s3 = Mock()
    bucket_name = 'example-bucket'

    mock_slack.channels.return_value = Channels([])
    mock_slack.user_data_json.return_value = 'user data body'

    run_backup(mock_slack, 'slack_channel_name', mock_s3, bucket_name)

    mock_s3.put_object.assert_has_calls([
        call(Body='user data body', Bucket=bucket_name, Key='users.json'),
        call(Body='[]', Bucket=bucket_name, Key='channels.json')
    ])


def test_channel_names_and_message_history_is_backed_up():
    mock_slack = Mock()
    mock_s3 = Mock()
    bucket_name = 'example-bucket'

    mock_slack.channels.return_value = Channels([{"name": "example-channel-name"}])
    mock_slack.user_data_json.return_value = 'user data body'
    mock_slack.channel_history.return_value = 'channel history body'

    run_backup(mock_slack, 'slack_channel_name', mock_s3, bucket_name)

    mock_s3.put_object.assert_has_calls([
        call(Body='user data body', Bucket=bucket_name, Key='users.json'),
        call(Body='[\n  {\n    "name": "example-channel-name"\n  }\n]', Bucket=bucket_name, Key='channels.json'),
        call(Body='channel history body', Bucket=bucket_name, Key='example-channel-name/example-channel-name.json')
    ])


def test_message_sent_to_slack_on_a_backup():
    mock_slack = Mock()
    mock_s3 = Mock()

    mock_slack.channels.return_value = Channels([])
    mock_slack.user_data_json.return_value = 'user data body'

    run_backup(mock_slack, 'slack_channel_name', mock_s3, 'example-bucket')

    mock_slack.post_to_channel.assert_called_once_with(
        channel='slack_channel_name',
        message=f'All public channels have been backed up to example-bucket'
    )

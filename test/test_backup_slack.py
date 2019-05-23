import random
import string
from itertools import repeat
from unittest.mock import Mock, call

from slackstorian.backup_slack import save_to_s3, save_channel, download_and_save_channels


def test_save_to_s3_calls_s3_client_with_correct_args():
    s3_stub = Mock()

    save_to_s3(s3_stub, 'example-bucket', "example-text ", "example-file")

    s3_stub.put_object.assert_called_once_with(
        Body='example-text ',
        Bucket='example-bucket',
        Key='example-file'
    )


def test_save_channel_saves_a_file_with_the_same_folder_name():
    s3_stub = Mock()
    save_channel(s3_stub, 'example-bucket', {'name': 'channel-name'}, 'example-text')

    s3_stub.put_object.assert_called_once_with(
        Body='example-text',
        Bucket='example-bucket',
        Key='channel-name/channel-name.json'
    )


def test_download_and_save_channels_saves_a_file_for_each_channel():
    channel_list = generate_channel_data()
    slack_mock = Mock(return_value='channel-history-json-body')
    s3_mock = Mock()

    download_and_save_channels(slack_mock, s3_mock, 'example-bucket-name', channel_list)

    slack_calls = []
    for channel in channel_list:
        slack_calls.append(call(channel=channel))
    slack_mock.channel_history.assert_has_calls(slack_calls)

    assert s3_mock.put_object.call_count == len(channel_list)


def generate_channel_data():
    number_of_channels = random.randint(0, 5)
    channels = list()

    for channel in repeat(None, number_of_channels):
        channels.append({
            "id": channel,
            "is_channel": bool(random.getrandbits(1)),
            "name": random.choice(string.ascii_letters)
        })

    return channels

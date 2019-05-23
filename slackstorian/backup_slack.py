#!/usr/bin/env python
# -*- encoding: utf-8
import time
from tqdm import tqdm

_USERNAMES_FILE_NAME = 'users.json'
_PUBLIC_CHANNELS_FILE_NAME = 'channels.json'


def save_to_s3(s3_client, bucket_name, file_body, filename):
    tqdm.write(f' uploading {filename} to s3')
    s3_client.put_object(
        Body=file_body,
        Bucket=bucket_name,
        Key=filename
    )
    tqdm.write(f'  done')


def save_channel(s3_client, bucket_name, channel_info, history_json_str):
    """Download the message history and save it to a JSON file."""

    # there must be a folder of the same name as the file to re import this back to slack
    channel_name = channel_info['name']
    aws_path = f'{channel_name}/{channel_name}.json'

    save_to_s3(s3_client, bucket_name, history_json_str, aws_path)


def download_and_save_channels(slack, s3_client, bucket_name, channels_list):
    for channel in tqdm(channels_list):
        history = slack.channel_history(channel=channel)
        save_channel(s3_client, bucket_name, channel, history)
        time.sleep(5) # dirty fix to get around rate limits ._.


def run_backup(slack, slack_channel_name, s3_client, s3_bucket_name):
    tqdm.write(f'Saving username list to {_USERNAMES_FILE_NAME}')
    save_to_s3(s3_client, s3_bucket_name, slack.user_data_json(), _USERNAMES_FILE_NAME)

    tqdm.write('Saving public channels to %s' % _PUBLIC_CHANNELS_FILE_NAME)
    channels = slack.channels()
    save_to_s3(s3_client, s3_bucket_name, channels.as_json(), _PUBLIC_CHANNELS_FILE_NAME)

    download_and_save_channels(slack=slack, s3_client=s3_client, bucket_name=s3_bucket_name, channels_list=channels.list)

    slack.post_to_channel(
        channel=slack_channel_name,
        message=f'All public channels have been backed up to {s3_bucket_name}'
    )

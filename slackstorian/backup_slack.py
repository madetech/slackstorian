#!/usr/bin/env python
# -*- encoding: utf-8

import argparse
import json
import os
import sys
import boto3
from environs import Env
from tqdm import tqdm

from slackstorian.slack_client import SlackClient

__version__ = '1.0.0'

_USERNAMES_FILE_NAME = 'users.json'
_PUBLIC_CHANNELS_FILE_NAME = 'channels.json'


def save_channel(channel_info, history_json_str, path):
    """Download the message history and save it to a JSON file."""

    # there must be a folder of the same name as the file to re import this back to slack
    channel_name = channel_info['name']
    aws_path = f'{channel_name}/{channel_name}.json'

    save_to_s3(history_json_str, aws_path)


def download_and_save_channels(slack, channels_list):
    for channel in tqdm(channels_list):
        history = slack.channel_history(channel=channel)
        save_channel(channel_info=channel, history_json_str=history, path=channel['name'])


def parse_args(prog, version):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='A tool for downloading message history from Slack.  This '
                    'tool downloads the message history for all your public '
                    'channels, private channels, and direct message threads.',
        epilog='If your team is on the free Slack plan, this tool can '
               'download your last 10,000 messages.  If your team is on a paid '
               'plan, this can download your entire account history.',
        prog=prog)

    parser.add_argument(
        '--version', action='version', version='%(prog)s ' + version)

    return parser.parse_args()


def save_to_s3(file_body, filename):
    s3 = boto3.client(
        's3',
        aws_access_key_id=get_env('aws_access_key_id'),
        aws_secret_access_key=get_env('aws_secret_access_key')
    )

    tqdm.write(f' uploading {filename} to s3')
    s3.put_object(
        Body=file_body,
        Bucket=get_env('bucket_name'),
        Key=filename
    )
    tqdm.write(f'  done')


def get_env(key):
    enviroment = Env()
    enviroment.read_env()
    return enviroment(key)


def run_backup(slack):
    tqdm.write(f'Saving username list to {_USERNAMES_FILE_NAME}')
    save_to_s3(slack.user_data_json(), _USERNAMES_FILE_NAME)
    tqdm.write('Saving public channels to %s' % _PUBLIC_CHANNELS_FILE_NAME)
    channels = slack.channels()
    save_to_s3(channels.as_json(), _PUBLIC_CHANNELS_FILE_NAME)
    download_and_save_channels(slack=slack, channels_list=channels.list)


def main(*foo):
    args = parse_args(prog=os.path.basename(sys.argv[0]), version=__version__)

    slack = SlackClient(token=get_env('slack_token'))
    run_backup(slack)

    slack.post_to_channel(
        channel=get_env('notification_channel'),
        message='All public channels have been backed up to %s' % get_env('bucket_name')
    )


if __name__ == '__main__':
    main()

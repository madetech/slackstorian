import os
import sys

import boto3
from environs import Env

from .backup_slack import run_backup
from .slack_client import SlackClient

import argparse

__version__ = '1.0.0'


def main(*foo):
    args = parse_args(prog=os.path.basename(sys.argv[0]), version=__version__)

    slack = SlackClient(token=get_env('slack_token'))

    s3_client = boto3.client(
        's3',
        aws_access_key_id=get_env('aws_access_key_id'),
        aws_secret_access_key=get_env('aws_secret_access_key')
    )

    run_backup(slack, s3_client, get_env('bucket_name'))

    slack.post_to_channel(
        channel=get_env('notification_channel'),
        message='All public channels have been backed up to %s' % get_env('bucket_name')
    )


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


def get_env(key):
    enviroment = Env()
    enviroment.read_env()
    return enviroment(key)


if __name__ == '__main__':
    main()

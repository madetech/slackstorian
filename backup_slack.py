#!/usr/bin/env python
# -*- encoding: utf-8

import argparse
import errno
import json
import os
import sys
import slacker
import boto3
from environs import Env
from tqdm import tqdm
import tempfile
__version__ = '1.0.0'

USERNAMES = 'users.json'
PUBLIC_CHANNELS = 'channels.json'

def download_history(channel_info, history, path):
    """Download the message history and save it to a JSON file."""
    path = os.path.join(path, '%s.json' % channel_info['name'])

    json_str = json.dumps(history, indent=2, sort_keys=True)

    aws_path = '%s/%s' % (channel_info['name'], os.path.basename(path))
    save_to_s3(json_str, aws_path)

def download_public_channels(slack, outdir):
    """Download the message history for the public channels where this user
    is logged in.
    """
    channels = slack.channels()
    json_str = json.dumps(channels, indent=2)

    save_to_s3(json_str, PUBLIC_CHANNELS)

    for channel in tqdm(channels):
        history = slack.channel_history(channel=channel)
        path = os.path.join(outdir, channel['name'])
        download_history(channel_info=channel, history=history, path=path)

def download_usernames(slack, path):
    """Download the username history from Slack."""
    json_str = json.dumps(slack.usernames, indent=2, sort_keys=True)

    save_to_s3(json_str, path)

class AuthenticationError(Exception):
    pass

class SlackHistory(object):
    """Wrapper around the Slack API.  This provides a few convenience
    wrappers around slacker.Slacker for the particular purpose of history
    download.
    """

    def __init__(self, token):
        self.slack = slacker.Slacker(token=token)

        # Check the token is valid
        try:
            self.slack.auth.test()
        except slacker.Error:
            raise AuthenticationError('Unable to authenticate API token.')

        self.usernames = self._fetch_user_mapping()

    def _get_history(self, channel_class, channel_id):
        """Returns the message history for a channel"""
        last_timestamp = None
        response = channel_class.history(channel=channel_id,
                                         latest=last_timestamp,
                                         oldest=0,
                                         count=1000)
        return response.body['messages']

    def _fetch_user_mapping(self):
        """Gets all user information"""
        return self.slack.users.list().body['members']

    def channels(self):
        """Returns a list of public channels."""
        return self.slack.channels.list().body['channels']

    def channel_history(self, channel):
        """Returns the message history for a channel."""
        return self._get_history(self.slack.channels, channel_id=channel['id'])

    def post_to_channel(self, channel, message):
        return self.slack.chat.post_message(
            channel=channel, text=message, username="Slackstorian"
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
    parser.add_argument(
        '--outdir', help='output directory', default='./backup')

    return parser.parse_args()

def save_to_s3(file_body, filename):
    s3 = boto3.client(
        's3',
        aws_access_key_id=env('aws_access_key_id'),
        aws_secret_access_key=env('aws_secret_access_key')
    )

    tqdm.write(f' uploading {filename} to s3')
    s3.put_object(
        Body=file_body,
        Bucket=env('bucket_name'),
        Key=filename
    )
    tqdm.write(f'  done')


def env(key):
    enviroment = Env()
    enviroment.read_env()
    return enviroment(key)

def main(*foo):

    args = parse_args(prog=os.path.basename(sys.argv[0]), version=__version__)

    try:
        slack = SlackHistory(token=env('slack_token'))
    except AuthenticationError as err:
        sys.exit(err)

    usernames = os.path.join(args.outdir, USERNAMES)
    tqdm.write(f'Saving username list to {usernames}')
    download_usernames(slack, path=usernames)

    public_channels = args.outdir
    tqdm.write('Saving public channels to %s' % public_channels)
    download_public_channels(slack, outdir=public_channels)

    # slack.post_to_channel(
    #     channel=env('notification_channel'),
    #     message='All public channels have been backed up to %s' % env('bucket_name')
    # )

if __name__ == '__main__':
    main()

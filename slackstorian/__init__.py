import boto3
from environs import Env

from slackstorian.backup_slack import run_backup
from slackstorian.slack_client import SlackClient


def main(*foo):
    slack = SlackClient(token=get_env('slack_token'))

    s3_client = boto3.client(
        's3',
        aws_access_key_id=get_env('aws_access_key_id'),
        aws_secret_access_key=get_env('aws_secret_access_key')
    )

    slack_channel_name = get_env('notification_channel')

    run_backup(slack, slack_channel_name, s3_client, get_env('bucket_name'))


def get_env(key):
    enviroment = Env()
    enviroment.read_env()
    return enviroment(key)


if __name__ == '__main__':
    main()

# Slackstorian

Slack backup tool, that uploads the history public channels history to S3 and posts an announcement in a channel of your choice when it's done.

## How to backup:
install [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation) and dependencies
```bash
poetry install
```


Set the following enviroment variables in `./.env`:
```
aws_access_key_id=ACCESS_KEY_ID
aws_secret_access_key=SECRET_ACCESS_KEY
bucket_name=BUCKET_NAME
slack_token=LEGACY_SLACK_TOKEN
notification_channel=CHANNEL_NAME
```
[Generate `LEGACY_SLACK_TOKEN` here](https://api.slack.com/custom-integrations/legacy-tokens)

Then run:
```
poetry run python lambda.py
```
By default the backups are saved in `./backup/` and uploaded into the defined bucket.

## How to restore:
Zip all the files in the defined bucket and use Slack's import tool, found here:
`https://[WORKSPACE_NAME].slack.com/services/import`

---
Inspired by https://github.com/alexwlchan/backup-slack
